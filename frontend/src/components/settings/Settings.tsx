import { Box, Button, Card, CardBody, CardHeader, Center, Flex, Heading, Input, Select, Text } from '@chakra-ui/react';
import { useEffect, useState } from 'react';
import { GetConfig, GetOpenaiModels, PostConfig } from '../../ApiService';
import { ConfigType, FullConfigType } from '../../dto';

export function Settings() {
  const [config, setConfig] = useState<FullConfigType | null>(null);
  const [initialConfig, setInitialConfig] = useState<FullConfigType | null>(null);
  const [models, setModels] = useState<string[]>(['']);

  useEffect(() => {
    GetConfig().then((r) => {
      setConfig(r);
      setInitialConfig(r);
    });
    GetOpenaiModels().then((r) => {
      setModels(r.models);
    });
  }, []);

  const hasChanged = JSON.stringify(config) !== JSON.stringify(initialConfig);

  const sendConfig = async () => {
    if (config) {
      const configToSend: ConfigType = {
        openai: config.openai,
      };

      const response = await PostConfig(configToSend);
      if (!response?.error) {
        setInitialConfig(config);
      }
    }
  };

  return (
    <Flex w={'100%'} justifyContent={'center'} align={'center'} gap={8} h={'100%'} flexDirection={'column'}>
      <Card w={'70%'} h={'70%'} bg={'main.100'} boxShadow={'lg'} align={'center'} p={8}>
        <CardHeader>
          <Heading>Openai</Heading>
        </CardHeader>
        <CardBody w={'100%'} h={'100%'}>
          <Flex h={'100%'} textAlign={'center'} justifyContent={'center'} flexDirection={'column'} gap={8}>
            <Box>
              <Text>API key</Text>
              <Input
                placeholder="OpenAI API key"
                w={'50%'}
                value={config?.openai?.api_key || ''}
                onChange={(e) =>
                  setConfig((prevConfig) =>
                    prevConfig ? { ...prevConfig, openai: { ...prevConfig.openai, api_key: e.target.value } } : null,
                  )
                }
              />
            </Box>
            <Box>
              <Text>Model</Text>
              <Center>
                <Select
                  w={'50%'}
                  value={config?.openai?.model || ''}
                  onChange={(e) =>
                    setConfig((prevConfig) =>
                      prevConfig ? { ...prevConfig, openai: { ...prevConfig.openai, model: e.target.value } } : null,
                    )
                  }
                >
                  {models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </Select>
              </Center>
            </Box>
          </Flex>
        </CardBody>
      </Card>
      {hasChanged && (
        <Box position="fixed" bottom="16px" right="16px">
          <Button bg={'main.400'} color={'white'} onClick={sendConfig}>
            Send Config
          </Button>
        </Box>
      )}
    </Flex>
  );
}
