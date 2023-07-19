<h1 align="center">AutoCertify</h1>

<p align="center">
  <img alt="badge-lastcommit" src="https://img.shields.io/github/last-commit/GaryHilares/AutoCertify?style=for-the-badge">
  <img alt="badge-openissues" src="https://img.shields.io/github/issues-raw/GaryHilares/AutoCertify?style=for-the-badge">
  <img alt="badge-license" src="https://img.shields.io/github/license/GaryHilares/AutoCertify?style=for-the-badge">
  <img alt="badge-contributors" src="https://img.shields.io/github/contributors/GaryHilares/AutoCertify?style=for-the-badge">
  <img alt="badge-codesize" src="https://img.shields.io/github/languages/code-size/GaryHilares/AutoCertify?style=for-the-badge">
</p>

## What is AutoCertify?
AutoCertify is a website that allows you to create, view, download and share verified or unverified certificates.

### Platforms
- Google Chrome
- Mozilla Firefox
- Microsoft Edge

### Dependencies
#### Development & Deployment
- Python
- pip
- MongoDB


## Motivation
As a past hackathon organizer, I had to devise workarounds for creating and delivering participation certificates myself twice, because similar alternatives were unavailable. I decided to code a more robust solution.

## Installation and usage
1. Install required dependencies:
    - You can find the latest Python release [here](https://www.python.org/downloads/).
    - You can find more information about how to install pip [here](https://pip.pypa.io/en/stable/installation/).
    - You can find more information about how to install MongoDB [here](https://www.mongodb.com/docs/manual/installation/). Alternatively, you can setup a MongoDB Atlas cluster in [their website](https://www.mongodb.com/atlas/database) and use it.
2. Download the project:
    - Using Git is recommended. If you have it, you may clone the repository using:

            git clone https://github.com/GaryHilares/Plain-Text-Encryption.git

    - You can also download the source code using [GitHub's GUI](https://github.com/GaryHilares/Plain-Text-Encryption/tree/main).
3. Install Python packages:
    - Open a terminal in the project's root and run:

            pip install -r requirements.txt

4. Configure the project:
    - Create a `.env` file following `.env.example`'s format and fill it with your own information.
    - You may also want to change the settings that are set by default by editing `config.py`.
5. Run the website:
    - You can start a local development server by opening a terminal in the project's root and running:

            python3 run.py

    - You can also run the tests with the following command:

            pytest tests/
    


## Contributors
Thanks to these wonderful people for making AutoCertify possible!

<p align="center"><a href="https://github.com/GaryHilares/AutoCertify/graphs/contributors"><img src="https://contrib.rocks/image?repo=GaryHilares/AutoCertify"></a></p>

## License
This work is licensed under a [Creative Commons Attribution 4.0 International License](https://github.com/GaryHilares/AutoCertify/blob/main/LICENSE).