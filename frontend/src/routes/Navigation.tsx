import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { MainTabs } from './MainTabs';

export function Navigation() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainTabs />} />
      </Routes>
    </BrowserRouter>
  );
}
