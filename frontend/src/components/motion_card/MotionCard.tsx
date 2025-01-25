import { Heading, Text } from '@chakra-ui/react';
import { FramerMotionCard } from '../../theme';

interface ClickableMotionCardInterface {
  heading: string;
  text: string;
}

export function MotionCard({ heading, text }: ClickableMotionCardInterface) {
  return (
    <FramerMotionCard
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.1 }}
      w={'400px'}
      h={'600px'}
      bg={'main.100'}
      boxShadow={'lg'}
      align={'center'}
      textAlign={'center'}
      justifyContent={'center'}
      p={2}
      color={'main.300'}
    >
      <Heading mb={8}>{heading}</Heading>
      <Text>{text}</Text>
    </FramerMotionCard>
  );
}
