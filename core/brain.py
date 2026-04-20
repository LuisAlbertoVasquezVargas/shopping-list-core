# core/brain.py

class Brain:
    def interpret(self, message):
        msg = message.lower().strip()
        
        if any(word in msg for word in ["add", "buy", "get"]):
            item = " ".join(message.split()[1:])
            return {"action": "ADD", "value": item}
            
        if any(word in msg for word in ["remove", "delete", "erase"]):
            try:
                item_id = int(message.split()[-1])
                return {"action": "DELETE", "value": item_id}
            except ValueError:
                return {"action": "ERROR", "value": "ID required for removal"}
                
        if any(word in msg for word in ["show", "list", "what"]):
            return {"action": "READ", "value": None}
            
        return {"action": "UNKNOWN", "value": message}
