export type FullConfigType = ConfigType & {
  assistants: AssistantsType;
};

export type ConfigType = {
  openai: openaiType;
};

export type homeAssistantType = {
  api_url: string;
  api_key: string;
};

export type openaiType = {
  api_key: string;
  model: string;
};

export type AssistantsType = {
  [name: string]: AssistantDataType;
};

export type AssistantDataType = {
  name: string;
  personality: string;
  language: string;
  wake_word: string;
  voice: string;
};

export type CustomCommandsTypeWithPythonAndShell = CustomCommandsTypeWithPython & {
  shell_script: string;
};

export type CustomCommandsTypeWithPython = {
  function_definition: CustomCommandsType;
  python_code: string;
};

export type CustomCommandsType = {
  name: string;
  description: string;
  parameters: ParametersType;
};

export type ParametersType = {
  type: JsonSchemaType;
  properties: ParameterPropertiesType;
  required: string[];
};

type ParameterPropertiesType = {
  [key: string]: {
    type: JsonSchemaType;
    description: string;
  };
};

export type JsonSchemaType = 'string' | 'number' | 'object' | 'array' | 'boolean' | 'null';
