# kb/services/importers/email_importer.py

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import email
from email.parser import BytesParser
from email.policy import default
import imaplib
import base64
from pathlib import Path
import logging

from .base import ImporterBase
from ...core.schemas import EntryType
 
logger = logging.getLogger(__name__)

class EmailImporter(ImporterBase):
    """Import emails from IMAP servers (Gmail, Outlook, etc.)"""
    
    def import_data(
        self,
        source: str,
        username: str,
        password: str,
        folder: str = "INBOX",
        since_date: Optional[datetime] = None,
        labels: Optional[List[str]] = None,
        sender_filter: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Import emails from IMAP server
        
        Args:
            source: IMAP server (e.g., 'imap.gmail.com')
            username: Email address
            password: App password (not regular password)
            folder: Email folder to import from
            since_date: Only import emails after this date
            labels: Gmail labels to filter by
            sender_filter: Only import from specific sender
            limit: Maximum emails to import
        
        Returns:
            Import statistics
        """
        
        stats = {
            'emails_found': 0,
            'emails_imported': 0,
            'emails_skipped': 0,
            'errors': []
        }
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(source)
            mail.login(username, password)
            
            # Select folder
            mail.select(folder)
            
            # Build search criteria
            search_criteria = ['ALL']
            
            if since_date:
                date_str = since_date.strftime("%d-%b-%Y")
                search_criteria = [f'SINCE {date_str}']
            
            if sender_filter:
                search_criteria.append(f'FROM "{sender_filter}"')
            
            # Gmail labels
            if labels and 'gmail' in source.lower():
                for label in labels:
                    search_criteria.append(f'X-GM-LABELS "{label}"')
            
            # Search
            search_str = ' '.join(search_criteria)
            status, messages = mail.search(None, search_str)
            
            if status != 'OK':
                raise Exception("Failed to search emails")
            
            email_ids = messages[0].split()
            stats['emails_found'] = len(email_ids)
            
            # Limit results
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            # Process emails
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        stats['emails_skipped'] += 1
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    email_message = BytesParser(policy=default).parsebytes(raw_email)
                    
                    # Extract data
                    subject = email_message['subject'] or "No Subject"
                    sender = email_message['from']
                    date_str = email_message['date']
                    email_date = email.utils.parsedate_to_datetime(date_str)
                    
                    # Get body
                    body = self._extract_email_body(email_message)
                    
                    # Create title
                    title = f"Email: {subject}"
                    
                    # Create content with metadata
                    content = f"""**From:** {sender}
**Date:** {email_date.strftime('%Y-%m-%d %H:%M:%S')}
**Subject:** {subject}

---

{body}
"""
                    
                    # Source metadata
                    source_metadata = {
                        'sender': sender,
                        'subject': subject,
                        'date': email_date.isoformat(),
                        'email_id': email_id.decode(),
                        'folder': folder
                    }
                    
                    # Determine tags
                    tags = ['email', 'imported']
                    if labels:
                        tags.extend(labels)
                    
                    # Extract sender domain for additional tagging
                    if '@' in sender:
                        domain = sender.split('@')[-1].strip('>')
                        tags.append(f"from-{domain.split('.')[0]}")
                    
                    # Create entry
                    entry = self.create_entry_from_import(
                        title=title,
                        content=content,
                        entry_type=EntryType.NOTE,
                        source='email_import',
                        source_metadata=source_metadata,
                        tags=tags
                    )
                    
                    if entry:
                        stats['emails_imported'] += 1
                    else:
                        stats['emails_skipped'] += 1
                
                except Exception as e:
                    stats['emails_skipped'] += 1
                    stats['errors'].append(f"Email {email_id}: {str(e)}")
                    logger.error(f"Failed to import email {email_id}: {e}")
            
            # Cleanup
            mail.close()
            mail.logout()
        
        except Exception as e:
            stats['errors'].append(f"Connection error: {str(e)}")
            logger.error(f"Email import failed: {e}")
        
        return stats
    
    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email"""
        
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                body = str(email_message.get_payload())
        
        return body.strip()
