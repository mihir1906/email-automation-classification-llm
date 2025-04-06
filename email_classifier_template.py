# Configuration and imports
import os
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Sample email dataset
sample_emails = [
    {
        "id": "001",
        "from": "angry.customer@example.com",
        "subject": "Broken product received",
        "body": "I received my order #12345 yesterday but it arrived completely damaged. This is unacceptable and I demand a refund immediately. This is the worst customer service I've experienced.",
        "timestamp": "2024-03-15T10:30:00Z"
    },
    {
        "id": "002",
        "from": "curious.shopper@example.com",
        "subject": "Question about product specifications",
        "body": "Hi, I'm interested in buying your premium package but I couldn't find information about whether it's compatible with Mac OS. Could you please clarify this? Thanks!",
        "timestamp": "2024-03-15T11:45:00Z"
    },
    {
        "id": "003",
        "from": "happy.user@example.com",
        "subject": "Amazing customer support",
        "body": "I just wanted to say thank you for the excellent support I received from Sarah on your team. She went above and beyond to help resolve my issue. Keep up the great work!",
        "timestamp": "2024-03-15T13:15:00Z"
    },
    {
        "id": "004",
        "from": "tech.user@example.com",
        "subject": "Need help with installation",
        "body": "I've been trying to install the software for the past hour but keep getting error code 5123. I've already tried restarting my computer and clearing the cache. Please help!",
        "timestamp": "2024-03-15T14:20:00Z"
    },
    {
        "id": "005",
        "from": "business.client@example.com",
        "subject": "Partnership opportunity",
        "body": "Our company is interested in exploring potential partnership opportunities with your organization. Would it be possible to schedule a call next week to discuss this further?",
        "timestamp": "2024-03-15T15:00:00Z"
    }
]


class EmailProcessor:
    def __init__(self):
        """Initialize the email processor with OpenAI API key."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define valid categories
        self.valid_categories = {
            "complaint", "inquiry", "feedback",
            "support_request", "other"
        }

    def validate_email(self, email: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate the email format and content.
        """
        required_fields = ["id", "from", "subject", "body", "timestamp"]

        for field in required_fields:
            if field not in email:
                return False, f"Missing field: {field}"
            
            if not isinstance(email[field], str):
                return False, f"Invalid value for field: {field}"
            
        try:
            datetime.fromisoformat(email["timestamp"].replace("Z", "+00:00"))   

        except ValueError:
            return False, "Invalid timestamp format"
        
        return True, None
            


    def classify_email(self, email: Dict) -> Optional[str]:
        """
        Classify an email using LLM.
        Returns the classification category or None if classification fails.
        
        TODO: 
        1. Design and implement the classification prompt
        2. Make the API call with appropriate error handling
        3. Validate and return the classification
        """

        prompt = ( 

            f"You are an intelligent email customer support assistant. Your task is to classify the following email into one of the categories: {', '.join(self.valid_categories)}.\n\n"
            f"Email Subject: {email.get('subject')}\n"
            f"Email Body: {email.get('body')}\n\n"
            f"Respond with only category name in lowercase.\n"
        )

        try:

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature = 0
            )

            category = response.choices[0].message.content.strip().lower()

            if category in self.valid_categories:
                logger.info(f"Email {email['id']} classified as: {category}")
                return category
            else:
                logger.warning(f"Invalid classification for email {email['id']}: {category}")
                return None

        except Exception as e:
            logger.error(f"Error during classification for email {email['id']}: {e}")
            return None
        

    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        """
        Generate an automated response based on email classification.
        
        TODO:
        1. Design the response generation prompt
        2. Implement appropriate response templates
        3. Add error handling
        """
        try:
            response_templates = {
                "complaint": f" Dear {email['from'],}, \n\n"
                            f"We're are sorry to hear about your experince. Our support team is already looking into this issue."
                            f"We truly care about your complaint and aim to resolve this as quickly as possible.\n\nBest Regards,\nSupport Team",

                "inquiry": f"Hi {email['from']}!,\n\n"
                           f"Thank you for reaching out with your question. We will get back to you shortly with the requested information.\n\nBest Regards,\nCustomer Experience Team",

                "feedback": f"Hi {email['from']}!,\n\n"
                            f"Thank you for your feedback! We appreciate your input and will take it into consideration. We are always thrilled to satisfy out customers.\n\n"
                            f"We will make sure to pass this along to the team.\n\nBest Regards,\nCustomer Success Team",

                "support_request": f"Hi {email['from']}!,\n\n"
                                   f"Thank you for reaching out and letting us know about your issues. Out technical team will review your case and follow up as soon as possible.\n\nBest Regards,\n Tech Support Team",
                "other": f"Hi {email['from']}!,\n\n"
                         f"Thank you for reaching out, We have received your message and will direct it to the right team. You'll hear from us soon.\n\nBest Regards,\nGeneral Inquiries Team" 
            }

            response = response_templates.get(classification)

            if response:
                logger.info(f"Generated response for email {email['id']}: {response}")
                return response
            
            else:
                logger.warning(f"No response template found for classification {classification}.")
                return None

        except Exception as e:
            logger.error(f"Error during response generation for email {email['id']}: {e}")
            return None
        


class EmailAutomationSystem:
    def __init__(self, processor: EmailProcessor):
        """Initialize the automation system with an EmailProcessor."""
        self.processor = processor
        self.response_handlers = {
            "complaint": self._handle_complaint,
            "inquiry": self._handle_inquiry,
            "feedback": self._handle_feedback,
            "support_request": self._handle_support_request,
            "other": self._handle_other
        }

    
    def process_email(self, email: Dict) -> Dict:
        """
        Process a single email through the complete pipeline.
        Returns a dictionary with the processing results.
        
        TODO:
        1. Implement the complete processing pipeline
        2. Add appropriate error handling
        3. Return processing results
        """
        result = {
        "email_id": email.get("id"),
        "success": False,
        "classification": None,
        "response_sent": False,
        "error": None
        }

        try:
            is_valid, error = self.processor.validate_email(email)
            if not is_valid:
                result["error"] = error
                return result
            
            classification = self.processor.classify_email(email)
            if not classification:
                result["error"] = "LLM Classification failed"
                return result
            
            result["classification"] = classification

            handler = self.response_handlers.get(classification)
            if handler:
                handler(email)
                result["response_sent"] = True
                result["success"] = True
            else:
                result["error"] = f"No handler found for {classification}"

        
        except Exception as e:
            result["error"] = str(e)
    
        return result

    def _handle_complaint(self, email: Dict):
        """
        Handle complaint emails.
        TODO: Implement complaint handling logic
        """
        response = self.processor.generate_response(email, "complaint")
        if response:
            send_complaint_response(email["id"], response)  # Mock function to send response
            create_urgent_ticket(email['id'], "complaint" , email["body"])
        

    def _handle_inquiry(self, email: Dict):
        """
        Handle inquiry emails.
        TODO: Implement inquiry handling logic
        """
        response = self.processor.generate_response(email, "inquiry")
        if response:
            send_standard_response(email["id"], response)

    def _handle_feedback(self, email: Dict):
        """
        Handle feedback emails.
        TODO: Implement feedback handling logic
        """
        response = self.processor.generate_response(email, "feedback")
        if response:
            log_customer_feedback(email, email["body"])


    def _handle_support_request(self, email: Dict):
        """
        Handle support request emails.
        TODO: Implement support request handling logic
        """
        response = self.processor.generate_response(email, "support_request")
        if response:
            send_standard_response(email["id"], response)
            create_support_ticket(email["id"], email["body"])

    def _handle_other(self, email: Dict):
        """
        Handle other category emails.
        TODO: Implement handling logic for other categories
        """
        response = self.processor.generate_response(email, "other")
        if response:
            send_standard_response(email["id"], response)

    
# Mock service functions
def send_complaint_response(email_id: str, response: str):
    """Mock function to simulate sending a response to a complaint"""
    logger.info(f"Sending complaint response for email {email_id}")
    # In real implementation: integrate with email service


def send_standard_response(email_id: str, response: str):
    """Mock function to simulate sending a standard response"""
    logger.info(f"Sending standard response for email {email_id}")
    # In real implementation: integrate with email service


def create_urgent_ticket(email_id: str, category: str, context: str):
    """Mock function to simulate creating an urgent ticket"""
    logger.info(f"Creating urgent ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def create_support_ticket(email_id: str, context: str):
    """Mock function to simulate creating a support ticket"""
    logger.info(f"Creating support ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def log_customer_feedback(email_id: str, feedback: str):
    """Mock function to simulate logging customer feedback"""
    logger.info(f"Logging feedback for email {email_id}")
    # In real implementation: integrate with feedback system


def run_demonstration():
    """Run a demonstration of the complete system."""
    # Initialize the system
    processor = EmailProcessor()
    automation_system = EmailAutomationSystem(processor)

    # Process all sample emails
    results = []
    for email in sample_emails:
        logger.info(f"\nProcessing email {email['id']}...")
        result = automation_system.process_email(email)
        results.append(result)

    # Create a summary DataFrame
    df = pd.DataFrame(results)
    print("\nProcessing Summary:")
    print(df[["email_id", "success", "classification", "response_sent"]])

    return df


# Example usage:
if __name__ == "__main__":
    results_df = run_demonstration()
