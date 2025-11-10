import random
import time
from .model_manager import model_manager

def generate_questions(text):
    try:
        print("🔄 Checking if models are ready...")
        
        # Wait for models to load (with timeout)
        start_time = time.time()
        while not model_manager.are_models_ready() and (time.time() - start_time) < 30:
            time.sleep(0.5)
        
        if not model_manager.are_models_ready():
            print("⚠️ Models not ready, using fallback generator")
            return generate_fallback_questions(text)
        
        qg_pipeline = model_manager.get_qg_pipeline()
        qa_pipeline = model_manager.get_qa_pipeline()
        
        print("📊 Processing text for question generation...")
        
        # Preprocess text - split into meaningful sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        print(f"📝 Found {len(sentences)} meaningful sentences")
        
        # Use only first 3 sentences to avoid timeout
        chunks = sentences[:3]
        questions = []

        for i, chunk in enumerate(chunks):
            print(f"🔍 Processing sentence {i+1}/{len(chunks)}")
            
            try:
                # Generate question
                input_text = f"generate question: {chunk}"
                outputs = qg_pipeline(input_text, max_length=128, num_return_sequences=1)
                
                if outputs:
                    question = outputs[0]["generated_text"].strip()
                    print(f"❓ Generated: {question}")
                    
                    # Get answer
                    try:
                        answer_result = qa_pipeline(question=question, context=chunk)
                        answer = answer_result["answer"]
                        if not answer or len(answer) < 2:
                            answer = extract_fallback_answer(chunk)
                    except:
                        answer = extract_fallback_answer(chunk)
                    
                    print(f"✅ Answer: {answer}")
                    
                    # Generate options
                    words = [w.strip('.,!?()[]{}"') for w in chunk.split() 
                            if len(w) > 3 and w.lower() != answer.lower()]
                    distractors = random.sample(words, min(3, len(words)))
                    options = distractors + [answer]
                    random.shuffle(options)
                    
                    questions.append({
                        "question": question,
                        "answer": answer,
                        "options": options
                    })
                    
            except Exception as e:
                print(f"❌ Error processing sentence: {e}")
                continue
        
        # If no questions generated, use fallback
        if not questions:
            questions = generate_fallback_questions(text)
        
        print(f"🎯 Generated {len(questions)} questions")
        return questions

    except Exception as e:
        print(f"🔥 Error in generate_questions: {e}")
        return generate_fallback_questions(text)

def extract_fallback_answer(text):
    """Extract a fallback answer from text"""
    words = [w.strip('.,!?()[]{}"') for w in text.split() if len(w) > 4]
    return random.choice(words) if words else "Information"

def generate_fallback_questions(text):
    """Generate simple questions when models fail"""
    print("🔄 Using fallback question generator")
    
    sample_questions = [
        "What is the main topic discussed in this document?",
        "What are the key points mentioned in the text?",
        "Which technology or concept is described?",
        "What problem does this content address?",
        "What are the benefits highlighted in the document?"
    ]
    
    sample_answers = [
        "Artificial Intelligence", "Machine Learning", "Technology", 
        "Data Analysis", "Computer Science", "Algorithms",
        "Neural Networks", "Deep Learning", "Automation"
    ]
    
    # Extract some keywords from text for more relevant answers
    keywords = [word for word in text.split() if len(word) > 5 and word[0].isupper()]
    if keywords:
        sample_answers.extend(keywords[:3])
    
    questions = []
    for i in range(min(3, len(sample_questions))):
        question = sample_questions[i]
        answer = random.choice(sample_answers)
        
        other_options = [opt for opt in sample_answers if opt != answer]
        distractors = random.sample(other_options, min(3, len(other_options)))
        options = distractors + [answer]
        random.shuffle(options)
        
        questions.append({
            "question": question,
            "answer": answer,
            "options": options
        })
    
    return questions