# Passport Translator

A Flask-based web application for translating Ukrainian international passports to Turkish, multilingual translation documents and images with additional features like named entity recognition (NER), and email notifications.

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
  - `Mistral AI` for image-to-text conversion
  - `SpaCy` for natural language processing
  - `Flask` for web framework
  - `ReportLab` for PDF generation
  - `NumPy` for numerical operations
  - `smtplib` for email handling

## Installation

### 1. Clone the repository:
```bash
git clone https://github.com/your-username/passport_translator.git
cd passport_translator
```
### 2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
### 3. Install the required packages:
1. Requirements.txt:
```bash
pip install -r requirements.txt
```
2. Download the SpaCy model:
```bash
python -m spacy download en_core_web_trf
```
3. Install PyTorch with GPU support (if applicable): Visit the [PyTorch installation page](https://pytorch.org/get-started/locally/) and follow the instructions to install the appropriate version for your system. For example:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
### 4. Set up environment variables in a .env file:
``` bash
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True
```
### 5. Run the application:
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


## Named Entity Recognition (NER) with SpaCy

The application uses the **spaCy English trf model (en_core_web_trf)** for named entity recognition. Below are the entity labels recognized by the model:


### Model Performance Metrics (en_core_web_trf)

| **Metric** | **Value** | **Description**                                                 |
|------------|-----------|-----------------------------------------------------------------|
| ENTS_P     | 90.08%    | Precision: How many of the detected entities were correct       |
| ENTS_R     | 90.30%    | Recall: How many of the actual entities were correctly detected |
| ENTS_F     | 90.19%    | F1-score: Harmonic mean of precision and recall                 |


| **Label**   | **Description**                   | **Examples**                                                |
|-------------|-----------------------------------|-------------------------------------------------------------|
| CARDINAL    | Numbers without units             | "three", "1000", "millions"                                 |
| DATE        | Calendar dates                    | "January 1", "2024", "last year"                            |
| EVENT       | Historical, cultural, or events   | "World War II", "the Assumption of the Blessed Virgin Mary" |
| FAC         | Infrastructure objects            | "Golden Gate Bridge", "The Bakhchisaray Palace"             |
| GPE         | Countries, cities, regions        | "Ukraine", "Crimea", "California"                           |
| LANGUAGE    | Names of languages                | "English", "Ukrainian"                                      |
| LAW         | Legal documents, statutes         | "Constitution", "Article 5", "The Civil Rights Act"         |
| LOC         | Natural locations                 | "Mount Everest", "the Crimean Mountains", "Sahara"          |
| MONEY       | Amounts of money with currency    | "$50", "10 euros", "one million yen"                        |
| NORP        | Nationalities, religious groups   | "Ukrainians", "Christians", "Slavic"                        |
| ORDINAL     | Positions in a sequence           | "first", "2nd", "third"                                     |
| ORG         | Companies, institutions           | "Google", "UN", "Harvard University"                        |
| PERCENT     | Percent values                    | "5%", "thirty percent"                                      |
| PERSON      | Given names, surnames             | "George Washington", "Bruno Pelletier"                      |
| PRODUCT     | Manufactured objects              | "iPhone", "Tesla Model S", "PlayStation"                    |
| QUANTITY    | Numbers with measurement units    | "5 kilograms", "30 miles"                                   |
| TIME        | Specific times of day             | "2 PM", "midnight", "noon"                                  |
| WORK_OF_ART | Titles of books, films, paintings | "Mona Lisa", "1000 and One Nights", "War and Peace"         |
