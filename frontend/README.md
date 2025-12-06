# MetaFlow Frontend

A cutting-edge, highly-interactive React + TypeScript + Tailwind frontend for MetaFlow.

## Tech Stack
- React (v18+)
- TypeScript
- TailwindCSS
- Zustand (State Management)
- Framer Motion (Animations)
- 21st.dev Components (Text Shimmer, Animated Hero, etc.)

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the mock WebSocket server (for development):
   ```bash
   npm run dev:server
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```

## Project Structure
- `src/components/hero`: Hero section components (Animated Hero, Text Shimmer)
- `src/components/prompt`: Prompt Builder and STT components
- `src/components/workflow`: Execution and Results page components
- `src/components/ui`: Reusable UI components (21st.dev integrations)
- `src/store`: Zustand store
- `src/hooks`: Custom hooks (useWebsocket)
- `dev-server`: Mock WebSocket server

## Notes
- The STT integration is currently mocked in `STTPanel.tsx`.
- The WebSocket server is mocked in `dev-server/mock-ws-server.js`.
- To connect to a real backend, update the WebSocket URL in `ExecutionPage.tsx` and API calls in `sdk.ts`.
