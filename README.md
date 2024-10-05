# Clash Royale League Deck Checker

## Table of Contents
1. [Introdution](#introduction)
2. [Features](#features)
3. [Dependencies](#dependencies)
4. [Installation](#installation)
5. [How to Use](#how-to-use)
6. [Credits](#credits)

## Introduction
This is a Python Tkinter Application that can check what competitive decks and ranked deck players have been using. Also checks what they have played against and how often they used each win condition.

## Features
- Displays 1v1 and Duels decks in players battle log and what they played against
- Displays score and average elixir cost of decks
- Displays Path of Legend deck with global ranking
- Displays Pie charts of win condition use rates for user and opponents.
- Save seached players into .csv file with add player button

## Dependencies
* Python
   * Version: 3.12.4
   * Description: Python is the programming language used to develop this script.
* matplotlib
   * Version: 3.9.1
   * Description: create Pie charts of Win condition userates.
* Pillow
   * Version: 10.4.0
   * Description: Image editing and displaying.
* python-dotenv
   * Version: 1.0.1
   * Description: To hide API Token


## Installation
1. Install Git (Windows)
   * Download the [Git installer for windows](https://gitforwindows.org/).
   * Run the installer and follow the prompts. Ensure to select the option to add Git to your system PATH during installation.
2. Run and Verify Git Installation
   ```sh
   git --version
   ```
3. Navigate to the directory where you want to clone the respository:
   ```sh
   cd Desktop
   ```
4. Clone the repository:
   ```sh
   git clone https://github.com/JustinT301/CRDeckScouter.git
   ```
5. Navigate to the Cloned Repository:
   ```sh
   cd CRDDeckScouter
   ```
6. Before running the code, ensure you have Python and Dependances installed:
   ```sh
   python --version
   ```
   If Python is not installed, it can be downloaded [here](https://www.python.org/downloads/release/python-3124/)
   ```sh
   pip install -r requirements.txt
   ```

7. Unpack images.zip into a folder called images

8. Run the Clash Royale Automation bot code:
   ```sh
   python main.py
   ```
## How to Use
1. Run the script:
   ```sh
   python main.py
   ```

## Credits
* Developed by:
   * Justin Turbyfill
* Date: August 2nd, 2024