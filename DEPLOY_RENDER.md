# PPALI - Render Deployment Guide

This guide describes how to deploy the **PPALI** server to [Render.com](https://render.com) for free.

## FAST TRACK (If you have a GitHub Account)

1.  **Push Code to GitHub**
    *   Create a new repository on GitHub.
    *   Push all the files in this folder (`PCA_PEAK_PICKED`) to that repository.
    *   Make sure `Dockerfile` is in the root of the repository.

2.  **Create Service on Render**
    *   Log in to [Render Dashboard](https://dashboard.render.com/).
    *   Click **New +** -> **Web Service**.
    *   Connect your GitHub account and select your PPALI repository.

3.  **Configure Service**
    *   **Name**: `ppali-server` (or any unique name)
    *   **Runtime**: Select **Docker** (This is important!)
    *   **Region**: Singapore or nearest to you.
    *   **Instance Type**: Free
    *   **Branch**: `main` (or `master`)
    *   **Auto-Deploy**: Yes (default)

    *   *Note: Ensure "Docker Command" settings are left empty or default, Render will automatically detect the Dockerfile.*

4.  **Deploy**
    *   Click **Create Web Service**.
    *   Render will start building. It might take 2-5 minutes initially.
    *   Once completed, you will get a URL like `https://ppali-server.onrender.com`.

## Verify Deployment

1.  Open the provided URL.
2.  You should see the PPALI interface.
3.  Upload an Excel/CSV file to test the analysis.

## Notes

*   **Free Tier**: The application will spin down (sleep) after inactivity. The first request after sleeping might take 30-50 seconds to load.
*   **Security**: The server is public. Anyone with the link can access it.
