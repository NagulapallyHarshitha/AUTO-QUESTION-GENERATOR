from transformers import pipeline
import threading
import time

class ModelManager:
    _instance = None
    _models_loaded = False
    _qg_pipeline = None
    _qa_pipeline = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            # Start loading models in background
            cls._instance._start_loading_models()
        return cls._instance
    
    def _start_loading_models(self):
        """Start loading models in a separate thread"""
        def load_models():
            print("🔄 Starting model loading in background...")
            try:
                # Load question generation model
                self._qg_pipeline = pipeline(
                    "text2text-generation", 
                    model="valhalla/t5-small-qg-hl"
                )
                print("✅ Question generation model loaded")
                
                # Load question answering model
                self._qa_pipeline = pipeline(
                    "question-answering",
                    model="distilbert-base-cased-distilled-squad"
                )
                print("✅ Question answering model loaded")
                
                self._models_loaded = True
                print("🎉 All models loaded successfully!")
                
            except Exception as e:
                print(f"❌ Error loading models: {e}")
                self._models_loaded = False
        
        # Start loading in background thread
        thread = threading.Thread(target=load_models)
        thread.daemon = True
        thread.start()
    
    def are_models_ready(self):
        return self._models_loaded
    
    def get_qg_pipeline(self):
        return self._qg_pipeline
    
    def get_qa_pipeline(self):
        return self._qa_pipeline

# Create global instance
model_manager = ModelManager()