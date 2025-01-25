import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Center,
  Checkbox,
  Divider,
  Flex,
  Grid,
  GridItem,
  Heading,
  IconButton,
  Input,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  Select,
  Spinner,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Textarea,
  Tr,
} from '@chakra-ui/react';
import { CodeiumEditor } from '@codeium/react-code-editor';
import { useEffect, useState } from 'react';
import { IoMdHelp } from 'react-icons/io';
import { CustomCommandsType, CustomCommandsTypeWithPythonAndShell, JsonSchemaType, ParametersType } from '../../dto';

interface CustomCommandCardProps {
  name: string;
  description: string;
  parameters: ParametersType;
  python_code: string;
  deleteCommand: (key: string) => void;
  saveCommand: (key: string, command: CustomCommandsTypeWithPythonAndShell) => void;
}

export function CustomCommandCard({
  name,
  description,
  parameters,
  python_code,
  deleteCommand,
  saveCommand,
}: CustomCommandCardProps) {
  const [command, setCommand] = useState<CustomCommandsType>({
    name,
    description,
    parameters,
  });
  const [generateCodePrompt, setGenerateCodePrompt] = useState<string>('');
  const [pythonCode, setPythonCode] = useState<string>(python_code);
  const [shellScript, setShellScript] = useState<string>('');
  const [parameterList, setParameterList] = useState(parameters?.properties || {});
  const [newParameter, setNewParameter] = useState<{
    name: string;
    type: JsonSchemaType;
    description: string;
  }>({
    name: '',
    type: 'string',
    description: '',
  });
  const [requiredList, setRequiredList] = useState<string[]>(parameters?.required || []);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    document.querySelectorAll('[aria-label="Codeium Logo"]').forEach((el) => el.remove());
  }, [generating]);

  const addParameter = () => {
    if (newParameter.name && newParameter.type) {
      setParameterList((prev: any) => ({
        ...prev,
        [newParameter.name]: {
          type: newParameter.type,
          description: newParameter.description,
        },
      }));
      setNewParameter({ name: '', type: 'string', description: '' });
    }
  };

  const removeParameter = (name: string) => {
    setParameterList((prev: any) => {
      const updatedList = { ...prev };
      delete updatedList[name];
      return updatedList;
    });
    setRequiredList((prev: any[]) => prev.filter((req: string) => req !== name));
  };

  const toggleRequired = (name: string) => {
    setRequiredList((prev: string[]) =>
      prev.includes(name) ? prev.filter((req: string) => req !== name) : [...prev, name],
    );
  };

  const saveCustomCommand = () => {
    const updatedCommand = {
      function_definition: {
        name: command.name,
        description: command.description,
        parameters: {
          type: 'object' as JsonSchemaType,
          properties: parameterList,
          required: requiredList,
        },
      },
      python_code: pythonCode,
      shell_script: shellScript,
    };

    saveCommand(name, updatedCommand);
  };

  function generateCode(prompt: string) {
    setGenerating(true);
    let updatedPrompt = `let updatedPrompt = Generate the complete code for the following prompt. 
    You must reply with the entire code, every single word of the script, with absolutely no exceptions. 
    Do not include any explanations or additional text. Reply only with the full code in this format 
    \\\`\\\`\\\`python\n code goes here \n\\\`\\\`\\\`. you must also include the pip install line like 
    this \\\`\\\`\\\`bash\n code goes here \n\\\`\\\`\\\`. Assume i dont have any pip packages, and you 
    must provide the command to install any package you use in the code. Prompt: ${prompt};`;

    if (pythonCode !== '') {
      updatedPrompt = updatedPrompt.concat(`\n\nCurrent code: ${pythonCode}`);
    }

    setPythonCode('');
    setShellScript('');

    const ws = new WebSocket(`wss://${window.location.hostname}:5000/generate_code`);

    let accumulatedData = '';

    ws.onopen = () => {
      ws.send(JSON.stringify({ prompt: updatedPrompt }));
    };

    ws.onmessage = (event) => {
      try {
        const model_payload = JSON.parse(event.data);
        if ('code' in model_payload) {
          accumulatedData += model_payload.code;

          const pythonBlockMatch = accumulatedData.match(/```python\n([\s\S]*?)\n```/);
          const bashBlockMatch = accumulatedData.match(/```bash\n([\s\S]*?)\n```/);

          if (pythonBlockMatch) {
            const pythonBlock = pythonBlockMatch[1];
            setPythonCode((prevCode: string) => prevCode.concat(pythonBlock));
            accumulatedData = accumulatedData.replace(pythonBlockMatch[0], '');
          }

          if (bashBlockMatch) {
            const bashBlock = bashBlockMatch[1];
            setShellScript((prevCode: string) => prevCode.concat(bashBlock));
            accumulatedData = accumulatedData.replace(bashBlockMatch[0], '');
          }
        }
      } catch (e) {
        console.error(e);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setGenerating(false);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      setGenerating(false);
    };
  }

  return (
    <Card w={'70%'} h={'70%'} bg={'main.100'} boxShadow={'lg'} align={'center'} p={8}>
      <CardHeader>
        <Heading>{command.name}</Heading>
      </CardHeader>
      <CardBody w={'100%'} h={'100%'}>
        <Flex h={'100%'} textAlign={'center'} justifyContent={'center'} flexDirection={'column'} gap={8}>
          <Accordion allowToggle>
            <AccordionItem>
              <AccordionButton>
                <Box as="span" flex="1" textAlign="left">
                  Python code
                </Box>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4}>
                <Flex gap={4} flexDir={'column'}>
                  <Box>
                    <Text>Generate code</Text>
                    <Textarea
                      placeholder="Explain what you want the code to do..."
                      w={'100%'}
                      onChange={(e: { target: { value: any } }) => {
                        setGenerateCodePrompt(e.target.value);
                      }}
                    />
                    <Button bg={'main.400'} color={'white'} mt={2} onClick={() => generateCode(generateCodePrompt)}>
                      Generate
                    </Button>
                  </Box>
                  {!generating ? (
                    <>
                      <Divider />
                      <CodeiumEditor
                        language="python"
                        theme="vs-dark"
                        value={pythonCode}
                        onChange={(value: any) => setPythonCode(value ?? '')}
                        defaultValue={pythonCode}
                      />
                      <Divider />
                      <Text>Required Libraries:</Text>
                      <CodeiumEditor
                        language="bash"
                        theme="vs-dark"
                        height="60px"
                        value={shellScript}
                        onChange={(value: any) => setShellScript(value || '')}
                        defaultValue={shellScript}
                      />
                    </>
                  ) : (
                    <Center>
                      <Spinner />
                    </Center>
                  )}
                </Flex>
              </AccordionPanel>
            </AccordionItem>
            <AccordionItem>
              <AccordionButton>
                <Box as="span" flex="1" textAlign="left">
                  Info
                </Box>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4}>
                <Box>
                  <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={1}>
                    <GridItem w="100%" display="flex" alignItems="center" justifyContent="center" />
                    <GridItem w="100%" display="flex" alignItems="center" justifyContent="center">
                      <Text>Function to call</Text>
                    </GridItem>
                    <GridItem w="100%" display="flex" alignItems="center" justifyContent="center">
                      <Popover>
                        <PopoverTrigger>
                          <IconButton
                            aria-label={'custom_wake_word_info'}
                            icon={<IoMdHelp fontSize={24} />}
                            bg={'main.400'}
                            color={'white'}
                          />
                        </PopoverTrigger>
                        <PopoverContent>
                          <PopoverArrow />
                          <PopoverCloseButton />
                          <PopoverHeader>Function to call</PopoverHeader>
                          <PopoverBody>
                            The name of the function to be called. Must be written exactly as it is in the code.
                          </PopoverBody>
                        </PopoverContent>
                      </Popover>
                    </GridItem>
                  </Grid>
                  <Input
                    placeholder="Function name (e.g., my_function)"
                    onChange={(e: { target: { value: any } }) => {
                      setCommand((prev: any) => ({
                        ...prev,
                        name: e.target.value,
                      }));
                    }}
                    defaultValue={name}
                  />
                </Box>
                <Box mt={2}>
                  <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={1}>
                    <GridItem w="100%" display="flex" alignItems="center" justifyContent="center" />
                    <GridItem w="100%" display="flex" alignItems="center" justifyContent="center">
                      <Text>Description</Text>
                    </GridItem>
                    <GridItem w="100%" display="flex" alignItems="center" justifyContent="center">
                      <Popover>
                        <PopoverTrigger>
                          <IconButton
                            aria-label={'custom_wake_word_info'}
                            icon={<IoMdHelp fontSize={24} />}
                            bg={'main.400'}
                            color={'white'}
                          />
                        </PopoverTrigger>
                        <PopoverContent>
                          <PopoverArrow />
                          <PopoverCloseButton />
                          <PopoverHeader>Description</PopoverHeader>
                          <PopoverBody>
                            Describe what the function does. This is needed for the assistant to understand the
                            function.
                          </PopoverBody>
                        </PopoverContent>
                      </Popover>
                    </GridItem>
                  </Grid>
                  <Textarea
                    placeholder="Description (e.g., Fetches data from my server)"
                    onChange={(e: { target: { value: any } }) => {
                      setCommand((prev: any) => ({
                        ...prev,
                        description: e.target.value,
                      }));
                    }}
                    defaultValue={description}
                  />
                </Box>
              </AccordionPanel>
            </AccordionItem>
            <AccordionItem>
              <AccordionButton>
                <Box as="span" flex="1" textAlign="left">
                  Parameters
                </Box>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4}>
                <Flex gap={4} flexDir={'column'}>
                  <Input
                    placeholder="Parameter Name (e.g., username)"
                    value={newParameter.name}
                    onChange={(e: { target: { value: any } }) =>
                      setNewParameter((prev: any) => ({
                        ...prev,
                        name: e.target.value,
                      }))
                    }
                  />
                  <Select
                    value={newParameter.type}
                    onChange={(e: { target: { value: string } }) =>
                      setNewParameter((prev: any) => ({
                        ...prev,
                        type: e.target.value as JsonSchemaType,
                      }))
                    }
                  >
                    <option value="string">String</option>
                    <option value="number">Number</option>
                    <option value="object">Object</option>
                    <option value="array">Array</option>
                    <option value="boolean">Boolean</option>
                    <option value="null">Null</option>
                  </Select>
                  <Input
                    placeholder="Parameter Description (e.g., The username of the person)"
                    value={newParameter.description}
                    onChange={(e: { target: { value: any } }) =>
                      setNewParameter((prev: any) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                  />
                  <Button bg={'main.400'} color={'white'} onClick={addParameter}>
                    Add
                  </Button>
                  <Box>
                    <TableContainer>
                      <Table variant="simple">
                        <Tbody>
                          {Object.keys(parameterList).map((paramName) => (
                            <Tr key={paramName}>
                              <Td>
                                <Text>
                                  {paramName} ({parameterList[paramName].type})
                                </Text>
                              </Td>
                              <Td>
                                <Checkbox
                                  isChecked={requiredList.includes(paramName)}
                                  onChange={() => toggleRequired(paramName)}
                                >
                                  Required
                                </Checkbox>
                              </Td>
                              <Td>
                                <Button bg={'main.200'} onClick={() => removeParameter(paramName)}>
                                  Remove
                                </Button>
                              </Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </Box>
                </Flex>
              </AccordionPanel>
            </AccordionItem>
          </Accordion>
        </Flex>
        <Divider m={4} />
        <Center gap={4}>
          <Button
            bg={'main.200'}
            onClick={() => {
              deleteCommand(command.name);
            }}
          >
            Delete Custom Command
          </Button>
          <Button bg={'main.400'} color={'white'} onClick={saveCustomCommand}>
            Save Custom Command
          </Button>
        </Center>
      </CardBody>
    </Card>
  );
}
