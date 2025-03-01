import { Button, Flex, useToast } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import {
  DeleteCustomCommand,
  GetCustomCommands,
  PostCustomCommand,
} from "../../ApiService";
import {
  CustomCommandsTypeWithPython,
  CustomCommandsTypeWithPythonAndShell,
  JsonSchemaType,
} from "../../dto";
import { CustomCommandCard } from "./CustomCommandCard";

export function CustomCommands() {
  const [commands, setCommands] = useState<CustomCommandsTypeWithPython[]>();
  const toast = useToast();

  useEffect(() => {
    GetCustomCommands().then((r) => {
      setCommands(r);
    });
  }, []);

  function addNewCommand() {
    const newCommand: CustomCommandsTypeWithPython = {
      function_definition: {
        name: "",
        description: "",
        parameters: {
          type: "object" as JsonSchemaType,
          properties: {},
          required: [],
        },
      },
      python_code: "",
    };
    setCommands((prevCommands) => [newCommand, ...(prevCommands || [])]);
  }

  async function deleteCommand(key: string) {
    const response = await DeleteCustomCommand(key);

    if (!response?.error) {
      const filteredCommands = commands?.filter((command) => {
        return (
          command.function_definition.name.toLowerCase() !== key.toLowerCase()
        );
      });

      setCommands(filteredCommands);
    }
  }

  async function saveCommand(
    key: string,
    command: CustomCommandsTypeWithPythonAndShell
  ) {
    const updatedCommands = commands?.map((cmd) => {
      if (cmd.function_definition.name.toLowerCase() === key.toLowerCase()) {
        return {
          ...cmd,
          name: command.function_definition.name,
          description: command.function_definition.description,
          parameters: command.function_definition.parameters,
        };
      }
      return cmd;
    });
    setCommands(updatedCommands);

    PostCustomCommand(command).then((r) => {
      if (!r?.error) {
        toast({
          title: "Command saved.",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
      } else {
        toast({
          title: "Error saving command.",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
      }
    });
  }

  return (
    <Flex
      w={"100%"}
      justifyContent={"center"}
      align={"center"}
      gap={8}
      h={"100%"}
      flexDirection={"column"}
    >
      <Button bg={"main.400"} color={"white"} onClick={addNewCommand}>
        New Custom Command
      </Button>
      {commands &&
        commands.map((command) => (
          <CustomCommandCard
            key={command.function_definition.name}
            name={command.function_definition.name}
            description={command.function_definition.description}
            parameters={command.function_definition.parameters}
            python_code={command.python_code}
            deleteCommand={deleteCommand}
            saveCommand={saveCommand}
          />
        ))}
    </Flex>
  );
}
