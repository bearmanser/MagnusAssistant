import { Box, Flex, Grid, GridItem } from '@chakra-ui/react';
import { useEffect, useState } from 'react';
import { MdErrorOutline, MdKeyboardArrowUp } from 'react-icons/md';
import './styles.css';

export function Interface() {
  const [transcription, setTranscription] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [listening, setListening] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [showScrollButton, setShowScrollButton] = useState(true);
  const [audioBuffer, setAudioBuffer] = useState<Uint8Array[]>([]);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const [sampleRate] = useState<number>(22050);
  const [audioQueue, setAudioQueue] = useState<(Uint8Array | Uint8Array[])[]>([]);
  const [isProcessingAudio, setIsProcessingAudio] = useState<boolean>(false);
  const [bufferTreshold, setBufferTreshold] = useState<number>(50);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setTranscription('');
      setResponse('');
      setError('');
    }, 60000);

    return () => clearTimeout(timeoutId);
  }, [response, transcription, error]);

  useEffect(() => {
    const context = new AudioContext();
    setAudioContext(context);

    function connectToWebSocketAndSendAudio() {
      const ws = new WebSocket(`wss://${window.location.hostname}:5000/ws`);
      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        console.log('WebSocket connection is open');
      };

      ws.onmessage = async (event) => {
        if (typeof event.data === 'string') {
          try {
            const model_payload = JSON.parse(event.data);

            if ('activation' in model_payload) {
              setListening(true);
            }

            if ('transcription' in model_payload) {
              setTranscription(model_payload['transcription']);
              setListening(false);
            }

            if ('response' in model_payload) {
              setResponse(model_payload['response']);
            }

            if ('stop_listening' in model_payload) {
              setListening(false);
            }

            if ('__END_OF_STREAM__' in model_payload) {
              setBufferTreshold(1);
            }
          } catch (e) {
            console.error(e);
          }
        } else if (event.data instanceof ArrayBuffer) {
          setBufferTreshold(50);
          const chunk = new Uint8Array(event.data);
          setAudioBuffer((prevBuffer) => [...prevBuffer, chunk]);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed');
        connectToWebSocketAndSendAudio();
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      function sendAudioData(audioData: string | ArrayBuffer | Blob | ArrayBufferView) {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(audioData);
        } else {
          setError('WebSocket connection failed.');
        }
      }

      function startCapture() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          navigator.mediaDevices
            .getUserMedia({ audio: true })
            .then(function (stream) {
              const audioContext = new AudioContext();
              const audioInput = audioContext.createMediaStreamSource(stream);
              const bufferSize = 8192;
              const recorder = audioContext.createScriptProcessor(bufferSize, 1, 1);

              recorder.onaudioprocess = function (event) {
                const samples = event.inputBuffer.getChannelData(0);
                const PCM16iSamples = samples.map((sample) => {
                  const val = Math.floor(32767 * sample);
                  return Math.min(32767, Math.max(-32768, val));
                });

                const int16Array = new Int16Array(PCM16iSamples);
                const blob = new Blob([int16Array], { type: 'application/octet-stream' });
                sendAudioData(blob);
              };

              audioInput.connect(recorder);
              recorder.connect(audioContext.destination);

              const sampleRate = audioContext.sampleRate;
              ws.send(sampleRate.toString());
            })
            .catch(function (err) {
              setError('Error capturing audio.');
            });
        } else {
          setError('getUserMedia is not supported.');
        }
      }

      startCapture();
    }

    connectToWebSocketAndSendAudio();

    return () => {
      if (context) {
        context.close();
      }
    };
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY == 0) {
        setShowScrollButton(true);
      } else {
        setShowScrollButton(false);
      }
    };
    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  useEffect(() => {
    console.log('Audio buffer length:', audioBuffer.length);
    if (audioBuffer.length >= bufferTreshold && !isPlaying && audioContext && !isProcessingAudio) {
      setIsProcessingAudio(true);
      const concatenatedBuffer = new Uint8Array(
        audioBuffer.reduce((acc: number[], val) => acc.concat(Array.from(val)), []),
      );
      setAudioBuffer([]);

      if (isPlaying) {
        setAudioQueue((prevQueue) => [...prevQueue, concatenatedBuffer]);
      } else {
        playAudio(concatenatedBuffer);
      }
    }
  }, [audioBuffer, audioContext, sampleRate, isPlaying, isProcessingAudio, bufferTreshold]);

  const playAudio = (buffer: Uint8Array | Uint8Array[]) => {
    const fadeDuration = 0.05;

    if (buffer instanceof Uint8Array) {
      buffer = [buffer];
    }

    const concatenatedBuffer = new Uint8Array(buffer.reduce((acc: number[], val) => acc.concat(Array.from(val)), []));
    const wavBuffer = createWavHeader(concatenatedBuffer, sampleRate);

    audioContext
      ?.decodeAudioData(wavBuffer.buffer)
      .then((decodedData) => {
        const source = audioContext.createBufferSource();
        const gainNode = audioContext.createGain();
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(1, audioContext.currentTime + fadeDuration);

        source.buffer = decodedData;
        source.connect(gainNode);
        gainNode.connect(audioContext.destination);
        setIsPlaying(true);
        source.start(0);

        const duration = decodedData.duration * 1000;

        setTimeout(
          () => {
            gainNode.gain.linearRampToValueAtTime(1, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + fadeDuration);
            setTimeout(() => {
              if (audioQueue.length > 0) {
                const nextAudio = audioQueue[0];
                setAudioQueue((prevQueue) => prevQueue.slice(1));
                playAudio(nextAudio);
              } else {
                setIsPlaying(false);
                setIsProcessingAudio(false);
              }
            }, fadeDuration * 1000);
          },
          duration - fadeDuration * 1000,
        );
      })
      .catch((error) => {
        console.error('Error decoding audio data:', error);
        setIsProcessingAudio(false);
      });
  };

  function createWavHeader(samples: Uint8Array, sampleRate: number) {
    const numChannels = 1;
    const bitsPerSample = 16;
    const blockAlign = (numChannels * bitsPerSample) / 8;
    const byteRate = sampleRate * blockAlign;
    const dataSize = samples.length;

    const buffer = new ArrayBuffer(44 + samples.length);
    const view = new DataView(buffer);

    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataSize, true);
    writeString(view, 8, 'WAVE');

    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);

    writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);

    const samplesView = new Uint8Array(buffer, 44);
    samplesView.set(samples);

    return new Uint8Array(buffer);
  }

  function writeString(view: DataView, offset: number, string: string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  return (
    <Flex
      direction="column"
      w="100%"
      h="100%"
      alignItems="center"
      justifyContent="center"
      style={{
        transition: 'background-color 0.3s ease-in-out',
        backgroundColor: showScrollButton ? 'var(--chakra-colors-main-200)' : 'black',
        cursor: showScrollButton ? 'auto' : 'none',
      }}
    >
      {showScrollButton && (
        <MdKeyboardArrowUp
          size={100}
          color={'var(--chakra-colors-main-400)'}
          onClick={() => {
            window.scrollTo({
              top: document.body.scrollHeight,
              behavior: 'smooth',
            });
          }}
        />
      )}
      <Flex w={'100%'} justifyContent={'end'} align={'center'} color={'red'} gap={4} mr={4}>
        {false && error && (
          <>
            {error}
            <MdErrorOutline />
          </>
        )}
      </Flex>
      <Grid templateColumns="repeat(3, 1fr)" gap={6} w={'100%'} h={'100%'}>
        <GridItem w="100%">
          <Box
            className={`mic ${listening ? 'listening' : ''}`}
          >
            <Box opacity={listening ? '100%' : '5%'} className="mic-shadow" />
          </Box>
        </GridItem>
      </Grid>
    </Flex>
  );
}
