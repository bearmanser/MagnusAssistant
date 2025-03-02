import { Box, Button, Flex, useToast } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { GetConfig } from "../../ApiService";
import { AssistantsType } from "../../dto";
import { AssistantCard } from "./AssistantCard";

export function AssistantConfiguration() {
  const [assistants, setAssistants] = useState<AssistantsType>({});
  const toast = useToast();

  useEffect(() => {
    GetConfig().then((r) => {
      if(!r.error){
        setAssistants(r.assistants);
      }else{
        toast({
          title: "Error getting assistants.",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
      }
    });
  }, []);

  const addNewAssistant = () => {
    setAssistants((prev) => ({
      [`${Object.keys(prev).length}`]: {
        name: "",
        personality: "",
        language: "English",
        wake_word: "magnus",
        voice: "",
      },
      ...prev,
    }));
  };

  if (assistants === undefined) {
    return <Box>Loading...</Box>;
  }

  function deleteAssistantFromData(key: string) {
    setAssistants((prev) => {
      const newAssistants = { ...prev };
      delete newAssistants[key];
      return newAssistants;
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
      <Button bg={"main.400"} color={"white"} onClick={addNewAssistant}>
        New assistant
      </Button>
      {Object.entries(assistants)
        .reverse()
        .map(([id, data]) => (
          <AssistantCard
            key={id}
            id={id}
            data={data}
            deleteAssistantFromData={deleteAssistantFromData}
          />
        ))}
    </Flex>
  );
}
