# kb/services/importers/chat_importer.py

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json
import logging

from .base import ImporterBase
from ...core.schemas import EntryType
 
logger = logging.getLogger(__name__)

class ChatExportImporter(ImporterBase):
    """Import chat conversations from Claude, ChatGPT, etc."""
    
    def import_data(
        self,
        source: Path,
        chat_format: str = 'auto',
        combine_conversations: bool = False,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Import chat exports
        
        Args:
            source: Path to export file or directory
            chat_format: 'claude', 'chatgpt', or 'auto'
            combine_conversations: Combine multi-turn conversations into one entry
            tags: Additional tags
        
        Returns:
            Import statistics
        """
        
        stats = {
            'conversations_found': 0,
            'conversations_imported': 0,
            'conversations_skipped': 0,
            'errors': []
        }
        
        source_path = Path(source)
        
        try:
            if source_path.is_file():
                # Single export file
                files = [source_path]
            else:
                # Directory of exports
                files = list(source_path.glob('*.json'))
            
            stats['conversations_found'] = len(files)
            
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Auto-detect format
                    if chat_format == 'auto':
                        if 'uuid' in data and 'name' in data:
                            detected_format = 'claude'
                        elif 'title' in data and 'mapping' in data:
                            detected_format = 'chatgpt'
                        else:
                            detected_format = 'generic'
                    else:
                        detected_format = chat_format
                    
                    # Parse based on format
                    if detected_format == 'claude':
                        result = self._import_claude_export(data, tags)
                    elif detected_format == 'chatgpt':
                        result = self._import_chatgpt_export(data, tags)
                    else:
                        result = self._import_generic_export(data, tags)
                    
                    if result:
                        stats['conversations_imported'] += 1
                    else:
                        stats['conversations_skipped'] += 1
                
                except Exception as e:
                    stats['conversations_skipped'] += 1
                    stats['errors'].append(f"{file.name}: {str(e)}")
                    logger.error(f"Failed to import {file}: {e}")
        
        except Exception as e:
            stats['errors'].append(f"Import failed: {str(e)}")
            logger.error(f"Chat import failed: {e}")
        
        return stats
    
    def _import_claude_export(self, data: Dict, tags: List[str]) -> bool:
        """Import Claude conversation export"""
        
        try:
            title = data.get('name', 'Untitled Conversation')
            conversation_id = data.get('uuid', '')
            created_at = data.get('created_at', '')
            updated_at = data.get('updated_at', '')
            
            # Build conversation content
            messages = data.get('chat_messages', [])
            content_parts = []
            
            for msg in messages:
                sender = msg.get('sender', 'unknown')
                text = msg.get('text', '')
                timestamp = msg.get('created_at', '')
                
                if sender == 'human':
                    content_parts.append(f"**You:** {text}\n")
                else:
                    content_parts.append(f"**Claude:** {text}\n")
            
            content = "\n".join(content_parts)
            
            # Add metadata header
            header = f"""# {title}

**Created:** {created_at}
**Updated:** {updated_at}
**Conversation ID:** {conversation_id}

---

"""
            full_content = header + content
            
            # Create entry
            source_metadata = {
                'conversation_id': conversation_id,
                'created_at': created_at,
                'updated_at': updated_at,
                'message_count': len(messages),
                'platform': 'claude'
            }
            
            entry_tags = ['chat', 'claude', 'imported']
            if tags:
                entry_tags.extend(tags)
            
            entry = self.create_entry_from_import(
                title=f"Chat: {title}",
                content=full_content,
                entry_type=EntryType.CHAT_EXPORT,
                source='claude_export',
                source_metadata=source_metadata,
                tags=entry_tags
            )
            
            return entry is not None
        
        except Exception as e:
            logger.error(f"Failed to import Claude conversation: {e}")
            return False
    
    def _import_chatgpt_export(self, data: Dict, tags: List[str]) -> bool:
        """Import ChatGPT conversation export"""
        
        try:
            title = data.get('title', 'Untitled Conversation')
            conversation_id = data.get('id', '')
            create_time = data.get('create_time', 0)
            update_time = data.get('update_time', 0)
            
            created_at = datetime.fromtimestamp(create_time).isoformat() if create_time else ''
            updated_at = datetime.fromtimestamp(update_time).isoformat() if update_time else ''
            
            # Parse mapping structure
            mapping = data.get('mapping', {})
            content_parts = []
            message_count = 0
            
            # Build conversation tree
            for node_id, node in mapping.items():
                message = node.get('message')
                if message and message.get('content'):
                    author = message.get('author', {}).get('role', 'unknown')
                    content_data = message.get('content', {})
                    
                    if isinstance(content_data, dict):
                        parts = content_data.get('parts', [])
                        text = '\n'.join(parts) if parts else ''
                    else:
                        text = str(content_data)
                    
                    if text:
                        if author == 'user':
                            content_parts.append(f"**You:** {text}\n")
                        elif author == 'assistant':
                            content_parts.append(f"**ChatGPT:** {text}\n")
                        message_count += 1
            
            content = "\n".join(content_parts)
            
            # Add metadata header
            header = f"""# {title}

**Created:** {created_at}
**Updated:** {updated_at}
**Conversation ID:** {conversation_id}

---

"""
            full_content = header + content
            
            # Create entry
            source_metadata = {
                'conversation_id': conversation_id,
                'created_at': created_at,
                'updated_at': updated_at,
                'message_count': message_count,
                'platform': 'chatgpt'
            }
            
            entry_tags = ['chat', 'chatgpt', 'imported']
            if tags:
                entry_tags.extend(tags)
            
            entry = self.create_entry_from_import(
                title=f"Chat: {title}",
                content=full_content,
                entry_type=EntryType.CHAT_EXPORT,
                source='chatgpt_export',
                source_metadata=source_metadata,
                tags=entry_tags
            )
            
            return entry is not None
        
        except Exception as e:
            logger.error(f"Failed to import ChatGPT conversation: {e}")
            return False
    
    def _import_generic_export(self, data: Dict, tags: List[str]) -> bool:
        """Import generic JSON chat format"""
        
        try:
            # Try to extract basic structure
            title = data.get('title') or data.get('name') or 'Imported Conversation'
            messages = data.get('messages') or data.get('chat_messages') or []
            
            content_parts = []
            for msg in messages:
                role = msg.get('role') or msg.get('sender') or 'unknown'
                text = msg.get('content') or msg.get('text') or ''
                
                content_parts.append(f"**{role.capitalize()}:** {text}\n")
            
            content = "\n".join(content_parts)
            
            if not content.strip():
                return False
            
            # Create entry
            entry_tags = ['chat', 'imported']
            if tags:
                entry_tags.extend(tags)
            
            entry = self.create_entry_from_import(
                title=f"Chat: {title}",
                content=content,
                entry_type=EntryType.CHAT_EXPORT,
                source='generic_chat_export',
                tags=entry_tags
            )
            
            return entry is not None
        
        except Exception as e:
            logger.error(f"Failed to import generic conversation: {e}")
            return False
