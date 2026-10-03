// Public API of the "core" module (P1).
// Other modules import only from "@/modules/core".
export { ThemePreview } from "./ThemePreview";
export { ChatPage } from "./workspace/ChatPage";
export { WorkspaceLayout } from "./workspace/WorkspaceLayout";
export { MessageList } from "./workspace/MessageList";
export { useChatStore, layoutFromResponse, mascotStateFromResponse } from "./chatStore";
export type { WorkspaceMode } from "./chatStore";
export { AppHeader, ChatInput, CyberHudFrame, HistoryButton, Icon, ICON_NAMES, StatusLabel } from "./ui";

export type { IconName } from "./ui";
export { api, chatApi, configureApiAuth, notifyApiAuthChanged, subscribeApiAuth, getApiAuthSnapshot, ApiError } from "./api";
export type { AuthAdapter } from "./api";
