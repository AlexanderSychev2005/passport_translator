# Passport Translator

A Flask-based web application for translating documents and images with additional features like named entity recognition (NER), document scanning, and email notifications.

## Features

1. **Ukrainian Passport Translation**: Translates Ukrainian international passports into Turkish.
2. **General Document Translation**: Translates documents and images from any language into English, with named entity recognition using SpaCy.
3. **Document Scanning**: Detects and extracts document boundaries from uploaded images.
4. **Changelog**: Tracks and displays changes made to translations.
5. **Email Notifications**: Sends emails with custom content.

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, SCSS, JS
- **Libraries**:
  - `OpenCV` for image processing
  - `SpaCy` for natural language processing
  - `Flask` for web framework
  - `ReportLab` for PDF generation
  - `NumPy` for numerical operations
  - `smtplib` for email handling

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/passport_translator.git
   cd passport_translator
    ```
2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Set up environment variables in a .env file:
    ```bash
    EMAIL_BACKEND=smtp
    EMAIL_HOST=smtp.example.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=your-email@example.com
    EMAIL_HOST_PASSWORD=your-password
    EMAIL_USE_TLS=True
    ```
4. Run the application:
    ```bash
    python main.py
    ```
   
## Usage
1. Ukrainian Passport Translation:  
- Upload an image of a Ukrainian passport.
- Choose the points that form a document boundaries to be translated.
- The application will translate the text into Turkish and generate you a pdf file.

2. General Document Translation:
- Upload an image or document in any language.
- Choose the points that form a document boundaries to be translated.
- The application will translate the text into English and highlight named entities.

## Changelog Feature
**There's a changelog feature that tracks changes made to translations for documents and pictures. You can view the changelog in the application.**

## Email Notifications
**The application can send email notifications with custom content. Make sure to configure your email settings in the .env file.**

