# BISMALLAH ETHIOBIZ APP INSHA'ALLAH

## Overview
**Bismillah EthioBiz** is a custom Frappe Application designed to tailor ERPNext for the Ethiopian market. It currently focuses on specific branding/theming capabilities, hardcopy letter management, and HR customizations, while enforcing strict role-based security.

## Features

### 1. Branding Customizer (EthioBiz Theme)
*   **Dynamic Theming**: An in-app configuration module to change the Desk's look and feel without code.
*   **Customizable Elements**:
    *   **Primary Color**: Updates buttons, links, and accents.
    *   **Navbar Colors**: Customize the top navigation bar background and text.
    *   **Background**: Set a global background color.
    *   **Custom CSS**: Inject raw CSS for advanced styling.
*   **Mechanism**: Changes are compiled into a server-side CSS file (`generated_theme.css`) that is automatically served to all users.

### 2. Letter Module
*   **Letter Log DocType**: A dedicated system to track physical Inbound/Outbound correspondence.
*   **Key Fields**: Reference Number, Sender/Recipient, Date, Digital Attachment (Image).
*   **Access Control**: Restricted to authorized roles.

### 3. HR & Employee Customizations (Ethiopian Context)
*   **ID Management**:
    *   Renamed "Passport Detail" -> **"ID Detail"**.
    *   Added **ID Type**: `Passport`, `National ID`, `Kebele ID`.
*   **Simplified View**: Hidden extraneous sections like "Health Insurance" for cleaner data entry.

### 4. Security & Roles
*   **New Role**: `Biz Service Administrator`.
*   **Strict Permissions**:
    *   **Workspace Creation**: RESTRICTED (System Manager only).
    *   **Company Creation**: RESTRICTED (System Manager only).
*   **Multi-Company**: Added `Company` field to **User DocType** for explicit access control.

### 5. UI/UX Enhancements
*   **Clean Interface**: Hides the standard "Help" dropdown.
*   **Optimized Defaults**: Pre-configured for a "Light" theme preference.

--- 

## Installation on EthioBiz.et Server

### Prerequisites
*   Access to the `ethiobiz.et` server via SSH.
*   Docker container running the Frappe Bench.

### Step-by-Step Installation

1.  **Access the Server**
    ```bash
    ssh user@ethiobiz.et
    ```

2.  **Upload the App**
    Copy the `bismillah_ethiobiz` folder to the `apps` directory of your bench.
    ```bash
    cd /workspace/frappe-bench/apps
    # Clone or copy folder here
    ```

3.  **Install the App**
    Execute inside the bench container:
    ```bash
    bench --site ethiobiz.et install-app bismillah_ethiobiz
    ```

4.  **Run Migrations**
    ```bash
    bench --site ethiobiz.et migrate
    bench --site ethiobiz.et clear-cache
    ```

5.  **Restart Services**
    ```bash
    bench restart
    ```

### Verification
1.  Log in to `https://ethiobiz.et`.
2.  Search for **"EthioBiz Theme"** in the awesome bar.
3.  Create a new theme, set a Primary Color (e.g., Red), check "Is Active", and Save.
4.  Reload the page to see the new color applied.
