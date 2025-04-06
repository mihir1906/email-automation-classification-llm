# LLM Integration Exercise: Email Classification and Automation

## Overview
In this exercise, you'll build a system that uses Large Language Models (LLMs) to classify incoming emails and automate responses based on the classification. This tests your ability to:
- Integrate LLMs into a Python workflow
- Design and refine prompts for reliable classification
- Implement error handling and reliability measures
- Create automated response systems

## Setup and Requirements

### Environment Setup
1. Create a new virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Requirements File (requirements.txt)
```
openai>=1.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

### Configuration
1. Create a `.env` file in your project root:
```
OPENAI_API_KEY=your_api_key_here
```

## Exercise Structure
The exercise is divided into four main parts:

### Part 1: Email Data Processing (10 minutes)
- Load and validate the provided mock email data
- Create functions to extract email data
- Implement basic data validation

### Part 2: LLM Integration (20 minutes)
- Design classification prompts
- Implement API calls
- Create classification system

### Part 3: Prompt Engineering (20 minutes)
- Analyze classification accuracy
- Identify and handle edge cases
- Document prompt iterations and improvements

### Part 4: Response Automation (10 minutes)
- Create response generation system
- Implement category-specific handling
- Add appropriate error handling and logging
