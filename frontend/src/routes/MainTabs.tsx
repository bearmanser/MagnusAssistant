import { Center, Tab, TabList, TabPanel, TabPanels, Tabs } from '@chakra-ui/react';
import { Interface } from '../components/interface/Interface';
import { Settings } from '../components/settings/Settings';
import { AssistantConfiguration } from '../components/assistant_configuration/AssistantConfiguration';
import { CustomCommands } from '../components/custom_commands/CustomCommands';

export function MainTabs() {
  return (
    <Tabs isFitted variant="line" h="100%" rounded="10px" borderColor="main.200">
      <TabList gap={2} bg="main.100" p={2}>
        {['INTERFACE', 'CUSTOM COMMANDS', 'ASSISTANT CONFIGURATION', 'SETTINGS'].map((key) => (
          <Tab
            key={key}
            _selected={{ borderColor: 'main.200' }}
            borderColor="main.100"
            bg="main.100"
            rounded="4px"
            borderBottomWidth={2}
          >
            {key}
          </Tab>
        ))}
      </TabList>
      <TabPanels h="100%">
        <TabPanel h="100%" p={0}>
          <Center h="100%" w="100%">
            <Interface />
          </Center>
        </TabPanel>
        <TabPanel>
          <CustomCommands />
        </TabPanel>
        <TabPanel>
          <Center>
            <AssistantConfiguration />
          </Center>
        </TabPanel>
        <TabPanel>
          <Center>
            <Settings />
          </Center>
        </TabPanel>
      </TabPanels>
    </Tabs>
  );
}
