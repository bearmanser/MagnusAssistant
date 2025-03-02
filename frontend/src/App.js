import { Box, ChakraProvider } from "@chakra-ui/react";
import { Navigation } from "./routes/Navigation";
import { theme } from "./theme";

export function App() {
  return (
    <ChakraProvider theme={theme}>
      <Box h={"100vh"}>
        <Navigation />
      </Box>
    </ChakraProvider>
  );
}
