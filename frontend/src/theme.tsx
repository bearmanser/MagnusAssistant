import { Card, extendTheme } from '@chakra-ui/react';
import { motion } from 'framer-motion';

export const theme = extendTheme({
  colors: {
    main: {
      100: '#faf4ea',
      200: '#e4d9cd',
      300: '#070201',
      400: '#B87333',
    },
  },
  fonts: {
    body: 'Gotham, sans-serif',
  },
  styles: {
    global: {
      'html, body': {
        fontSize: '18px',
        bg: 'main.200',
        color: 'main.300',
      },
      '::-webkit-scrollbar': {
        width: '0px',
        background: 'transparent',
      },
      '::-webkit-scrollbar-thumb': {
        display: 'none',
      },
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: '500',
        borderRadius: '3xl',
      },
    },
  },
});

export const FramerMotionCard = motion(Card);
