import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Center,
  Checkbox,
  Divider,
  Flex,
  Heading,
  IconButton,
  Input,
  LinkOverlay,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  Select,
  Text,
  Textarea,
  useToast,
} from '@chakra-ui/react';
import { ChangeEvent, useEffect, useState } from 'react';
import { IoMdHelp } from 'react-icons/io';
import { IoVolumeMediumSharp } from 'react-icons/io5';
import { DeleteAssistant, GetVoices, GetVoiceSample, PostAssistantData } from '../../ApiService';
import { AssistantDataType } from '../../dto';

interface AssistantCardProps {
  id: string;
  data: AssistantDataType;
  deleteAssistantFromData: (id: string) => void;
}

export function AssistantCard({ id, data, deleteAssistantFromData }: AssistantCardProps) {
  const [useCustomWakeWord, setUseCustomWakeWord] = useState<boolean>(data.wake_word !== 'magnus');
  const [useCustomVoice, setUseCustomVoice] = useState<boolean>(false);
  const [voices, setVoices] = useState<{ [key: string]: any }[]>([]);
  const [voice, setVoice] = useState<any>(undefined);
  const [language, setLanguage] = useState<string>('English');
  const [config, setConfig] = useState<AssistantDataType>(data);
  const [wakeWordFiles, setWakeWordFiles] = useState<File[]>([]);
  const [voiceOnnxFile, setVoiceOnnxFile] = useState<File | undefined>();
  const [voiceJsonFile, setVoiceJsonFile] = useState<File | undefined>();
  const toast = useToast();

  useEffect(() => {
    GetVoices().then((r) => {
      if (r.error) {
        toast({
          title: 'Error getting voices.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      } else {
        const voicesArray = Array.isArray(r) ? r : Object.values(r);
        setVoices(voicesArray);
        const initialVoice = voicesArray.find((v) => v.key.split('.onnx')[0] === config.voice);
        setVoice(initialVoice);
      }
    });
  }, []);

  function playSample() {
    if (voices === undefined || voice === undefined) {
      return;
    }
    GetVoiceSample(voice).then((r: HTMLAudioElement | { error: string }) => {
      if (r.error) {
        toast({
          title: 'Error playing sample.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      } else if (r instanceof Blob) {
        const audioUrl = URL.createObjectURL(r);
        const audio = new Audio(audioUrl);
        audio.play().then();
      }
    });
  }

  function saveAssistant() {
    const formData = new FormData();

    if (wakeWordFiles.length > 0) {
      wakeWordFiles.forEach((file, index) => {
        formData.append(`${id}_wakeWordFile_${index}`, file);
      });
    }

    if (voiceOnnxFile && voiceJsonFile) {
      formData.append('voiceOnnxFile', voiceOnnxFile);
      formData.append('voiceJsonFile', voiceJsonFile);
    }

    formData.append('assistant_data', JSON.stringify({ [id]: config }));
    PostAssistantData(formData).then((r)=>{
      if (!r?.error) {
        toast({
          title: "Assistant saved.",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
      } else {
        toast({
          title: "Error saving assistant.",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
      }
    });
  }

  async function deleteAssistant() {
    const response = await DeleteAssistant(id);

    if (!response?.error) {
      deleteAssistantFromData(id);
    }
  }

  return (
    <Card w={'70%'} h={'70%'} bg={'main.100'} boxShadow={'lg'} align={'center'} p={8}>
      <CardHeader>
        <Heading>{config.name}</Heading>
      </CardHeader>
      <CardBody w={'100%'} h={'100%'}>
        <Flex h={'100%'} textAlign={'center'} justifyContent={'center'} flexDirection={'column'} gap={8}>
          <Box>
            <Text>Name</Text>
            <Input
              placeholder="Name"
              w={'50%'}
              onChange={(e) => {
                setConfig((prev) => ({ ...prev, name: e.target.value }));
              }}
              defaultValue={data.name}
            />
          </Box>
          <Box>
            <Text>Language</Text>
            <Center>
              <Select
                value={config.language}
                w={'50%'}
                onChange={(e: ChangeEvent<HTMLSelectElement>) => {
                  setLanguage(e.target.value);
                  setConfig((prev) => ({ ...prev, language: e.target.value }));
                }}
              >
                {voices &&
                  [...new Set(Object.values(voices).map((voice: any) => voice.language.name_english))].map(
                    (uniqueLanguage, index) => (
                      <option key={index} value={uniqueLanguage}>
                        {uniqueLanguage}
                      </option>
                    ),
                  )}
              </Select>
            </Center>
          </Box>
          <Box>
            <Text>Personality</Text>
            <Textarea
              placeholder="Personality"
              w={'50%'}
              onChange={(e) => setConfig((prev) => ({ ...prev, personality: e.target.value }))}
              defaultValue={data.personality}
            />
          </Box>
          <Box>
            <Text>Wake word</Text>
            <Flex w={'100%'}>
              {useCustomWakeWord ? (
                <Flex w={'50%'} ml={'25%'} borderWidth={1} rounded={8} align={'center'} p={2} gap={2}>
                  {'onnx:'}
                  <input
                    type="file"
                    id="wakeWordFileInput"
                    name="wakeWordFileInput"
                    multiple
                    onChange={(e) => {
                      e.target.files && setWakeWordFiles(Array.from(e.target.files));
                      setConfig((prev) => ({ ...prev, wake_word: id }));
                    }}
                  />
                </Flex>
              ) : (
                <Select
                  w={'50%'}
                  ml={'25%'}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) => {
                    setConfig((prev) => ({ ...prev, wake_word: e.target.value }));
                  }}
                  defaultValue={'magnus'}
                >
                  <option value={'magnus'}>Magnus</option>
                </Select>
              )}
              <Popover>
                <PopoverTrigger>
                  <IconButton
                    aria-label={'custom_wake_word_info'}
                    icon={<IoMdHelp fontSize={24} />}
                    bg={'main.400'}
                    color={'white'}
                    ml={4}
                  />
                </PopoverTrigger>
                <PopoverContent>
                  <PopoverArrow />
                  <PopoverCloseButton />
                  <PopoverHeader>Custom wake word</PopoverHeader>
                  <PopoverBody>
                    {'You can create a custom wake word in the '}
                    <LinkOverlay
                      href={
                        'https://colab.research.google.com/drive/' +
                        '1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing' +
                        '#scrollTo=1cbqBebHXjFD'
                      }
                      color="blue"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      wake word training environment.
                    </LinkOverlay>
                  </PopoverBody>
                </PopoverContent>
              </Popover>
              <Checkbox
                ml={4}
                bg={'main.400'}
                p={2}
                rounded={'full'}
                color={'white'}
                isChecked={useCustomWakeWord}
                onChange={() => {
                  setUseCustomWakeWord(!useCustomWakeWord);
                }}
              >
                Custom
              </Checkbox>
            </Flex>
          </Box>
          <Box>
            <Text>Wake word sensitivity</Text>
            <Input
              placeholder="0.5 usally works well"
              type='number'
              w={'50%'}
              onChange={(e) => {
                setConfig((prev) => ({ ...prev, wake_word_sensitivity: parseFloat(e.target.value) }));
              }}
              defaultValue={data.wake_word_sensitivity}
            />
          </Box>
          <Box>
            <Text>Voice</Text>
            <Flex w={'100%'}>
              {!useCustomVoice ? (
                <>
                  <Select
                    w={'50%'}
                    ml={'25%'}
                    onChange={(e: ChangeEvent<HTMLSelectElement>) => {
                      const selectedVoice = voices.find((voice) => voice.key === e.target.value);
                      setVoice(selectedVoice);
                      setConfig((prev) => ({ ...prev, voice: selectedVoice?.key.split('.onnx')[0] }));
                    }}
                    value={config.voice.split('.onnx')[0]}
                  >
                    <option>Select a voice</option>
                    {voices &&
                      voices.map(
                        (_voice: any, key: number) =>
                          _voice['language']['name_english'] === language && (
                            <option key={key} value={_voice['key']}>
                              {_voice['name']} ({_voice['language']['country_english']}) - {_voice['quality']} quality
                            </option>
                          ),
                      )}
                  </Select>

                  <IconButton
                    aria-label={'play_sample'}
                    icon={<IoVolumeMediumSharp fontSize={24} />}
                    bg={'main.400'}
                    color={'white'}
                    onClick={() => {
                      playSample();
                    }}
                    ml={4}
                  />
                </>
              ) : (
                <Flex w={'50%'} ml={'25%'} borderWidth={1} rounded={8} p={2} gap={2} align={'center'}>
                  {'onnx:'}
                  <input
                    type="file"
                    id="VoiceOnnxFileInput"
                    name="VoiceOnnxFileInput"
                    onChange={(e) => e.target.files && setVoiceOnnxFile(e.target.files[0])}
                  />
                  {'json:'}
                  <input
                    type="file"
                    id="VoiceJsonFileInput"
                    name="VoiceJsonFileInput"
                    onChange={(e) => e.target.files && setVoiceJsonFile(e.target.files[0])}
                  />
                </Flex>
              )}
              <Checkbox
                ml={4}
                bg={'main.400'}
                p={2}
                rounded={'full'}
                color={'white'}
                isChecked={useCustomVoice}
                onChange={() => {
                  setUseCustomVoice(!useCustomVoice);
                }}
              >
                Custom
              </Checkbox>
            </Flex>
          </Box>
        </Flex>
        <Divider m={4} />
        <Center gap={4}>
          <Button bg={'main.200'} onClick={deleteAssistant}>
            Delete Assistant
          </Button>
          <Button bg={'main.400'} color={'white'} onClick={saveAssistant}>
            Save Assistant
          </Button>
        </Center>
      </CardBody>
    </Card>
  );
}
