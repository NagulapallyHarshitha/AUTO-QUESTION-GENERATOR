from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import random
import PyPDF2
from docx import Document
import re
from collections import Counter
import hashlib

app = Flask(__name__)
app.secret_key = 'docuquest-secret-key-2024'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store document analysis in memory
document_data = {}

# Mock user database
users = {
    'admin@docuquest.com': {'password': 'admin123', 'name': 'Admin User'},
    'test@docuquest.com': {'password': 'test123', 'name': 'Test User'},
    'user@docuquest.com': {'password': 'user123', 'name': 'Demo User'}
}

def extract_text_from_pdf(file_path):
    """Extract real text from PDF files"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract real text from Word documents"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"❌ DOCX extraction error: {e}")
        return ""

def extract_text_from_txt(file_path):
    """Extract real text from text files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ TXT extraction error: {e}")
            return ""

def extract_text(file_path):
    """Extract text based on file type"""
    print(f"🔍 Extracting text from: {file_path}")
    
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        text = extract_text_from_txt(file_path)
    else:
        text = ""
    
    print(f"📄 Extracted {len(text)} characters")
    return text

def analyze_document_content(text):
    """Deep analysis of document content"""
    # Clean the text
    text = re.sub(r'\s+', ' ', text)
    
    # Split into sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 15]
    
    content_analysis = {
        'key_concepts': [],
        'definitions': [],
        'processes': [],
        'facts': [],
        'comparisons': [],
        'applications': [],
        'examples': [],
        'advantages': [],
        'disadvantages': [],
        'features': [],
        'sentences': sentences,
        'full_text': text
    }
    
    # Extract key concepts (capitalized words that appear multiple times)
    words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    concept_counts = Counter(words)
    
    # Filter out common words
    common_words = {'The', 'This', 'That', 'These', 'Those', 'There', 'What', 'When', 
                   'Where', 'Which', 'Who', 'How', 'Why', 'With', 'From', 'Have', 'Has'}
    
    content_analysis['key_concepts'] = [
        concept for concept, count in concept_counts.most_common(20) 
        if count >= 1 and concept not in common_words and len(concept) > 3
    ]
    
    # If no concepts found, use important words from text
    if not content_analysis['key_concepts']:
        all_words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_counts = Counter(all_words)
        content_analysis['key_concepts'] = [
            word.title() for word, count in word_counts.most_common(15) 
            if count > 1
        ]
    
    # Ensure we have at least some concepts
    if not content_analysis['key_concepts']:
        content_analysis['key_concepts'] = ['Document', 'Content', 'Information', 'Analysis', 'Data', 'Process', 'System', 'Method']
    
    # Categorize sentences
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Definitions
        if any(phrase in sentence_lower for phrase in [' is ', ' means ', ' refers to ', ' defined as ', ' known as ']):
            content_analysis['definitions'].append(sentence)
        # Processes
        elif any(word in sentence_lower for word in ['process', 'method', 'technique', 'approach', 'procedure', 'steps', 'how to']):
            content_analysis['processes'].append(sentence)
        # Comparisons
        elif any(word in sentence_lower for word in ['compared to', 'different from', 'similar to', 'versus', 'than', 'however']):
            content_analysis['comparisons'].append(sentence)
        # Applications
        elif any(word in sentence_lower for word in ['application', 'used for', 'purpose', 'utilized', 'applied']):
            content_analysis['applications'].append(sentence)
        # Examples
        elif any(word in sentence_lower for word in ['example', 'for instance', 'such as', 'including']):
            content_analysis['examples'].append(sentence)
        # Advantages
        elif any(word in sentence_lower for word in ['advantage', 'benefit', 'strength', 'positive']):
            content_analysis['advantages'].append(sentence)
        # Disadvantages
        elif any(word in sentence_lower for word in ['disadvantage', 'limitation', 'drawback', 'negative']):
            content_analysis['disadvantages'].append(sentence)
        # Features
        elif any(word in sentence_lower for word in ['feature', 'characteristic', 'property', 'attribute']):
            content_analysis['features'].append(sentence)
        # Facts (any substantial sentence)
        elif len(sentence.split()) > 6:
            content_analysis['facts'].append(sentence)
    
    print(f"✅ Analysis complete: {len(content_analysis['key_concepts'])} key concepts, {len(sentences)} sentences")
    return content_analysis

def generate_questions_batch(content_analysis, difficulty, batch_size=10, used_questions=None):
    """Generate a batch of questions for a specific difficulty"""
    if used_questions is None:
        used_questions = set()
    
    questions = []
    key_concepts = content_analysis['key_concepts']
    sentences = content_analysis['sentences']
    
    print(f"🔧 Generating {batch_size} {difficulty} questions from {len(key_concepts)} concepts")
    
    if not key_concepts or not sentences:
        return questions
    
    if difficulty == 'basic':
        templates = [
            "What is the main purpose of '{}' according to the document?",
            "What does the document specifically mention about '{}'?",
            "According to the text, what is '{}' primarily used for?",
            "What key information is provided about '{}' in the document?",
            "How is '{}' described in the content?",
            "What role does '{}' play based on the document's explanation?",
            "What is the significance of '{}' mentioned in the text?",
            "How does the document characterize '{}'?",
            "What aspect of '{}' is discussed in the document?",
            "What does the document say regarding '{}'?"
        ]
        
        for concept in key_concepts:
            if len(questions) >= batch_size:
                break
                
            question_text = random.choice(templates).format(concept)
            if question_text in used_questions:
                continue
            
            # Find relevant sentences for this concept
            relevant_sentences = [s for s in sentences if concept.lower() in s.lower()]
            
            # Use the most relevant sentence or create context-based explanation
            if relevant_sentences:
                explanation = relevant_sentences[0]
            else:
                # Find any sentence that might be relevant
                for sentence in sentences:
                    words_in_sentence = re.findall(r'\b\w+\b', sentence.lower())
                    if concept.lower() in words_in_sentence:
                        explanation = sentence
                        break
                else:
                    explanation = f"The document discusses {concept} and its importance in the context."
            
            # Generate realistic options based on document content
            other_concepts = [c for c in key_concepts if c != concept]
            distractors = random.sample(other_concepts, min(3, len(other_concepts)))
            
            # Ensure options are meaningful
            options = distractors + [concept]
            random.shuffle(options)
            
            questions.append({
                'question': question_text,
                'answer': concept,
                'options': options,
                'explanation': f"📖 According to the document: {explanation}",
                'difficulty': 'basic',
                'type': 'factual'
            })
            used_questions.add(question_text)
    
    elif difficulty == 'medium':
        templates = [
            "Based on the document, what best describes '{}'?",
            "How is '{}' defined in the context of this document?",
            "What method or approach is associated with '{}' according to the text?",
            "What process involves '{}' as described in the document?",
            "How does the document explain the function of '{}'?",
            "What specific technique is mentioned in relation to '{}'?",
            "According to the document, what procedure utilizes '{}'?",
            "How is '{}' implemented based on the document's description?",
            "What approach does the document suggest for '{}'?",
            "What does the document specify about the usage of '{}'?"
        ]
        
        for concept in key_concepts:
            if len(questions) >= batch_size:
                break
                
            question_text = random.choice(templates).format(concept)
            if question_text in used_questions:
                continue
            
            # Find definition or process content
            definition_sentences = [s for s in content_analysis['definitions'] if concept.lower() in s.lower()]
            process_sentences = [s for s in content_analysis['processes'] if concept.lower() in s.lower()]
            
            if definition_sentences:
                explanation = definition_sentences[0]
            elif process_sentences:
                explanation = process_sentences[0]
            else:
                relevant_sentences = [s for s in sentences if concept.lower() in s.lower()]
                explanation = relevant_sentences[0] if relevant_sentences else f"The document provides detailed information about {concept} and its implementation."
            
            other_concepts = [c for c in key_concepts if c != concept]
            distractors = random.sample(other_concepts, min(3, len(other_concepts)))
            options = distractors + [concept]
            random.shuffle(options)
            
            questions.append({
                'question': question_text,
                'answer': concept,
                'options': options,
                'explanation': f"📚 Document Insight: {explanation}",
                'difficulty': 'medium',
                'type': 'comprehension'
            })
            used_questions.add(question_text)
    
    elif difficulty == 'advanced':
        templates = [
            "What are the key advantages of '{}' mentioned in the document?",
            "How does '{}' compare to other approaches discussed in the text?",
            "What limitations or challenges does the document associate with '{}'?",
            "What real-world applications of '{}' are described in the document?",
            "How does '{}' differ from similar concepts in the document?",
            "What strategic importance does '{}' hold according to the analysis?",
            "What are the documented benefits of implementing '{}'?",
            "How does the document evaluate the effectiveness of '{}'?",
            "What critical analysis does the document provide about '{}'?",
            "What implications does the document suggest regarding '{}'?"
        ]
        
        for concept in key_concepts:
            if len(questions) >= batch_size:
                break
                
            question_text = random.choice(templates).format(concept)
            if question_text in used_questions:
                continue
            
            # Find analytical content
            advantage_sentences = [s for s in content_analysis['advantages'] if concept.lower() in s.lower()]
            comparison_sentences = [s for s in content_analysis['comparisons'] if concept.lower() in s.lower()]
            application_sentences = [s for s in content_analysis['applications'] if concept.lower() in s.lower()]
            
            if advantage_sentences:
                explanation = advantage_sentences[0]
            elif comparison_sentences:
                explanation = comparison_sentences[0]
            elif application_sentences:
                explanation = application_sentences[0]
            else:
                relevant_sentences = [s for s in sentences if concept.lower() in s.lower()]
                explanation = relevant_sentences[0] if relevant_sentences else f"The document analyzes {concept} from multiple perspectives including its applications and strategic value."
            
            other_concepts = [c for c in key_concepts if c != concept]
            distractors = random.sample(other_concepts, min(3, len(other_concepts)))
            options = distractors + [concept]
            random.shuffle(options)
            
            questions.append({
                'question': question_text,
                'answer': concept,
                'options': options,
                'explanation': f"🔍 Analytical Finding: {explanation}",
                'difficulty': 'advanced',
                'type': 'analysis'
            })
            used_questions.add(question_text)
    
    print(f"✅ Generated {len(questions)} {difficulty} questions")
    return questions

def initialize_document_questions(content_analysis, document_id):
    """Initialize questions for all difficulty levels"""
    document_data[document_id] = {
        'content_analysis': content_analysis,
        'used_questions': {
            'basic': set(),
            'medium': set(),
            'advanced': set()
        },
        'generated_questions': {
            'basic': [],
            'medium': [],
            'advanced': []
        },
        'stats': {
            'word_count': len(content_analysis['full_text'].split()),
            'sentence_count': len(content_analysis['sentences']),
            'key_concepts': len(content_analysis['key_concepts']),
            'file_type': 'DOCUMENT'
        }
    }
    
    # Generate initial batches for all difficulty levels
    for difficulty in ['basic', 'medium', 'advanced']:
        new_questions = generate_questions_batch(
            content_analysis, 
            difficulty, 
            batch_size=10,
            used_questions=document_data[document_id]['used_questions'][difficulty]
        )
        document_data[document_id]['generated_questions'][difficulty] = new_questions
        for q in new_questions:
            document_data[document_id]['used_questions'][difficulty].add(q['question'])
    
    print(f"🎯 Initialized {sum(len(q) for q in document_data[document_id]['generated_questions'].values())} total questions")

# Routes
@app.route("/")
def home():
    """Home page"""
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation
        if not email or not password:
            return render_template("login.html", error="Please enter both email and password")
        
        if email in users and users[email]['password'] == password:
            session['user'] = email
            session['user_name'] = users[email]['name']
            return redirect(url_for('analyzer'))
        else:
            return render_template("login.html", error="Invalid email or password. Please try again.")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logout user"""
    session.pop('user', None)
    session.pop('user_name', None)
    return redirect(url_for('home'))

@app.route("/analyzer", methods=["GET", "POST"])
def analyzer():
    """Main analyzer application"""
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    global document_data
    
    if request.method == "POST":
        print("📥 Form submitted!")
        
        file = request.files.get("document")
        
        if file and file.filename:
            print(f"📄 Processing file: {file.filename}")
            
            # Ensure uploads directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            print("💾 File saved successfully")
            
            text = extract_text(file_path)
            print(f"📝 Text length: {len(text)}")
            
            if text and len(text.strip()) > 50:
                content_analysis = analyze_document_content(text)
                
                document_id = hashlib.md5(text.encode()).hexdigest()[:10]
                
                initialize_document_questions(content_analysis, document_id)
                
                print(f"✅ Document analysis complete. Document ID: {document_id}")
                
                # Clean up uploaded file
                try:
                    os.remove(file_path)
                    print("🗑 Temporary file cleaned up")
                except:
                    pass
                
                return render_template("index.html", 
                                     document_id=document_id,
                                     document_stats=document_data[document_id]['stats'],
                                     user_name=session.get('user_name'))
            else:
                error = "❌ The document doesn't contain enough readable text. Please try a different file."
                return render_template("index.html", error=error, user_name=session.get('user_name'))
        else:
            error = "❌ Please select a file to upload."
            return render_template("index.html", error=error, user_name=session.get('user_name'))
    
    # GET request - show empty form
    return render_template("index.html", user_name=session.get('user_name'))

@app.route("/get_questions/<document_id>/<difficulty>")
def get_questions(document_id, difficulty):
    """Get questions for a specific difficulty"""
    global document_data
    
    print(f"🔍 Fetching questions for document {document_id}, difficulty {difficulty}")
    
    if document_id in document_data:
        questions = document_data[document_id]['generated_questions'].get(difficulty, [])
        print(f"✅ Found {len(questions)} questions for {difficulty} level")
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions),
            'has_more': len(document_data[document_id]['content_analysis']['key_concepts']) > 0
        })
    else:
        print(f"❌ Document {document_id} not found")
        return jsonify({
            'success': False,
            'error': 'Document not found. Please upload the document again.'
        })

@app.route("/more_questions/<document_id>/<difficulty>")
def more_questions(document_id, difficulty):
    """Generate more questions for a specific difficulty"""
    global document_data
    
    print(f"🔍 Generating more questions for document {document_id}, difficulty {difficulty}")
    
    if document_id in document_data:
        content_analysis = document_data[document_id]['content_analysis']
        used_questions = document_data[document_id]['used_questions'][difficulty]
        
        new_questions = generate_questions_batch(
            content_analysis,
            difficulty,
            batch_size=5,
            used_questions=used_questions
        )
        
        # Add new questions to stored questions
        document_data[document_id]['generated_questions'][difficulty].extend(new_questions)
        for q in new_questions:
            used_questions.add(q['question'])
        
        print(f"✅ Generated {len(new_questions)} new questions for {difficulty} level")
        
        return jsonify({
            'success': True,
            'new_questions': new_questions,
            'total_count': len(document_data[document_id]['generated_questions'][difficulty]),
            'has_more': len(content_analysis['key_concepts']) > len(used_questions) / 3
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        })

# Feature Pages
@app.route('/feature/unlimited-questions')
def unlimited_questions():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('unlimited_questions.html', user_name=session.get('user_name'))

@app.route('/feature/three-levels')
def three_levels():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('three_levels.html', user_name=session.get('user_name'))

@app.route('/feature/real-time-generation')
def real_time_generation():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('real_time_generation.html', user_name=session.get('user_name'))

@app.route('/feature/dynamic-generation')
def dynamic_generation():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dynamic_generation.html', user_name=session.get('user_name'))

if __name__ == "__main__":
    print("🚀 Starting DOCUQUEST - Professional Document Analyzer...")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔑 Test credentials: admin@docuquest.com / admin123")
    app.run(debug=True, host='0.0.0.0', port=8000, use_reloader=False)