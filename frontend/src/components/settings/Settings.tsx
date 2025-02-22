import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Center,
  Flex,
  Heading,
  HStack,
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
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { GetConfig, GetOpenaiModels, PostConfig } from "../../ApiService";
import { ConfigType, FullConfigType } from "../../dto";
import { IoMdHelp } from "react-icons/io";

export function Settings() {
  const [config, setConfig] = useState<FullConfigType | null>(null);
  const [initialConfig, setInitialConfig] = useState<FullConfigType | null>(
    null
  );
  const [models, setModels] = useState<string[]>([""]);

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
        twilio: config.twilio,
      };

      const response = await PostConfig(configToSend);
      if (!response?.error) {
        setInitialConfig(config);
      }
    }
  };

  return (
    <Flex
      w={"100%"}
      justifyContent={"center"}
      align={"center"}
      gap={8}
      h={"100%"}
      flexDirection={"column"}
    >
      <Card
        w={"70%"}
        h={"70%"}
        bg={"main.100"}
        boxShadow={"lg"}
        align={"center"}
        p={8}
      >
        <CardHeader>
          <Heading>Openai</Heading>
        </CardHeader>
        <CardBody w={"100%"} h={"100%"}>
          <Flex
            h={"100%"}
            textAlign={"center"}
            justifyContent={"center"}
            flexDirection={"column"}
            gap={8}
          >
            <Box>
              <Text>API key</Text>
              <Input
                placeholder="OpenAI API key"
                w={"50%"}
                value={config?.openai?.api_key || ""}
                onChange={(e) =>
                  setConfig((prevConfig) =>
                    prevConfig
                      ? {
                          ...prevConfig,
                          openai: {
                            ...prevConfig.openai,
                            api_key: e.target.value,
                          },
                        }
                      : null
                  )
                }
              />
            </Box>
            <Box>
              <Text>Model</Text>
              <Center>
                <Select
                  w={"50%"}
                  value={config?.openai?.model || ""}
                  onChange={(e) =>
                    setConfig((prevConfig) =>
                      prevConfig
                        ? {
                            ...prevConfig,
                            openai: {
                              ...prevConfig.openai,
                              model: e.target.value,
                            },
                          }
                        : null
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
      <Card
        w={"70%"}
        h={"70%"}
        bg={"main.100"}
        boxShadow={"lg"}
        align={"center"}
        p={8}
      >
        <CardHeader>
          <HStack>
            <Heading>Twilio</Heading>
            <Popover>
              <PopoverTrigger>
                <IconButton
                  aria-label={"Twilio help"}
                  icon={<IoMdHelp fontSize={24} />}
                  bg={"main.400"}
                  color={"white"}
                  ml={4}
                />
              </PopoverTrigger>
              <PopoverContent>
                <PopoverArrow />
                <PopoverCloseButton />
                <PopoverHeader>Twilio</PopoverHeader>
                <PopoverBody>
                  You can leave the Twilio fields empty if you don't want to
                  talk to your assistant via phone calls. See GitHub for
                  more information.
                </PopoverBody>
              </PopoverContent>
            </Popover>
          </HStack>
        </CardHeader>
        <CardBody w={"100%"} h={"100%"}>
          <Flex
            h={"100%"}
            textAlign={"center"}
            justifyContent={"center"}
            flexDirection={"column"}
            gap={8}
          >
          <Box>
            <Text>Assisant</Text>
            <Center>
              <Select
                w={"50%"}
                value={config?.twilio?.assistant || ""}
                onChange={(e) =>
                  setConfig((prevConfig) =>
                    prevConfig
                      ? {
                          ...prevConfig,
                          twilio: {
                            ...prevConfig.twilio,
                            assistant: e.target.value,
                          },
                        }
                      : null
                  )
                }
              >
                {config && Object.entries(config.assistants).map(([key, model]) => (
                  <option key={key} value={key}>
                    {model.name}
                  </option>
                ))}
              </Select>
            </Center>
          </Box>
            <Box>
              <Text>Base URL</Text>
              <Input
                placeholder="Twilio base URL"
                w={"50%"}
                value={config?.twilio?.base_url || ""}
                onChange={(e) =>
                  setConfig((prevConfig) =>
                    prevConfig
                      ? {
                          ...prevConfig,
                          twilio: {
                            ...prevConfig.twilio,
                            base_url: e.target.value,
                          },
                        }
                      : null
                  )
                }
              />
            </Box>
            <Box>
              <Text>Account SID</Text>
              <Center>
                <Input
                  placeholder="Twilio account SID"
                  w={"50%"}
                  value={config?.twilio?.account_sid || ""}
                  onChange={(e) =>
                    setConfig((prevConfig) =>
                      prevConfig
                        ? {
                            ...prevConfig,
                            twilio: {
                              ...prevConfig.twilio,
                              account_sid: e.target.value,
                            },
                          }
                        : null
                    )
                  }
                />
              </Center>
            </Box>
            <Box>
              <Text>Auth token</Text>
              <Center>
                <Input
                  placeholder="Twilio auth token"
                  w={"50%"}
                  value={config?.twilio?.auth_token || ""}
                  onChange={(e) =>
                    setConfig((prevConfig) =>
                      prevConfig
                        ? {
                            ...prevConfig,
                            twilio: {
                              ...prevConfig.twilio,
                              auth_token: e.target.value,
                            },
                          }
                        : null
                    )
                  }
                />
              </Center>
            </Box>
          </Flex>
        </CardBody>
      </Card>
      {hasChanged && (
        <Box position="fixed" bottom="16px" right="16px">
          <Button bg={"main.400"} color={"white"} onClick={sendConfig}>
            Save Config
          </Button>
        </Box>
      )}
    </Flex>
  );
}
