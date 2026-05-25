import { createBrowserRouter } from "react-router-dom";

import { LayoutShell } from "../components/layout-shell";
import { ApplicationTrackerPage } from "../pages/application-tracker-page";
import { DashboardPage } from "../pages/dashboard-page";
import { JobsFeedPage } from "../pages/jobs-feed-page";
import { LogsPage } from "../pages/logs-page";
import { ResumeUploadPage } from "../pages/resume-upload-page";
import { SettingsPage } from "../pages/settings-page";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LayoutShell />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "resume-upload", element: <ResumeUploadPage /> },
      { path: "jobs-feed", element: <JobsFeedPage /> },
      { path: "applications", element: <ApplicationTrackerPage /> },
      { path: "settings", element: <SettingsPage /> },
      { path: "logs", element: <LogsPage /> }
    ]
  }
]);
