# backend/api/chat_parser_embedding.py
"""
Parser conversacional basado en embeddings y similitud semántica
Usa TF-IDF o embeddings simples para mejor comprensión del contexto
"""

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Optional


class ChatParserEmbedding:
    """
    Parser basado en embeddings y similitud semántica
    Usa TF-IDF para encontrar patrones similares
    """
    
    def __init__(self):
        # Templates de ejemplos para cada tipo de caso
        self.templates = {
            'gaming': [
                "quiero jugar videojuegos",
                "pc para gaming",
                "computadora para juegos",
                "gamer pc"
            ],
            'development': [
                "programar código",
                "desarrollo de software",
                "programación python java",
                "developer workstation"
            ],
            'design': [
                "diseño gráfico",
                "editar imágenes",
                "render 3d",
                "photoshop illustrator"
            ],
            'office': [
                "oficina trabajo",
                "excel word",
                "documentos hojas cálculo",
                "trabajo básico"
            ],
            'video_editing': [
                "editar video",
                "premiere pro",
                "edición de video",
                "after effects"
            ]
        }
        
        # Vectorizador TF-IDF
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=1000
        )
        
        # Entrenar vectorizador con templates
        all_texts = []
        for templates_list in self.templates.values():
            all_texts.extend(templates_list)
        self.vectorizer.fit(all_texts)
        
        # Keywords (mismo que otros parsers)
        self.game_keywords = {
            'valorant': ['valorant', 'valor ant'],
            'fortnite': ['fortnite', 'fort nite'],
            'cyberpunk': ['cyberpunk', 'cyber punk', 'cyberpunk 2077'],
            'gta': ['gta', 'grand theft auto', 'gta 5', 'gta v'],
            'minecraft': ['minecraft', 'mine craft'],
            'lol': ['lol', 'league of legends', 'league'],
            'cod': ['call of duty', 'cod', 'warzone'],
            'apex': ['apex', 'apex legends'],
            'dota': ['dota', 'dota 2'],
            'csgo': ['cs go', 'counter strike', 'cs:go', 'cs2'],
            'overwatch': ['overwatch'],
            'fifa': ['fifa', 'fc 24', 'fc24'],
            'elden ring': ['elden ring'],
            'hogwarts': ['hogwarts legacy', 'hogwarts'],
            'starfield': ['starfield'],
            'baldurs gate': ['baldurs gate', "baldur's gate", 'bg3']
        }
        
        self.software_keywords = {
            'python': ['python', 'django', 'flask'],
            'java': ['java', 'spring'],
            'javascript': ['javascript', 'js', 'node', 'react', 'angular', 'vue'],
            'csharp': ['c#', 'csharp', '.net', 'unity'],
            'photoshop': ['photoshop', 'ps'],
            'illustrator': ['illustrator', 'ai'],
            'premiere': ['premiere', 'premiere pro'],
            'after effects': ['after effects', 'ae'],
            'blender': ['blender', '3d'],
            'autocad': ['autocad', 'cad'],
            'solidworks': ['solidworks'],
            'visual studio': ['visual studio', 'vs code', 'vscode'],
            'android studio': ['android studio'],
            'docker': ['docker', 'kubernetes'],
            'machine learning': ['machine learning', 'ml', 'tensorflow', 'pytorch', 'keras']
        }
        
        self.performance_patterns = {
            'high': ['ultra', 'máxima', 'maxima', 'alto rendimiento', 'high', 'best', 'potente'],
            'mid': ['medio', 'media', 'medium', 'balanced', 'balanceado'],
            'budget': ['básico', 'basico', 'barato', 'económico', 'budget', 'cheap', 'low']
        }
    
    def extract_budget(self, text: str) -> Optional[int]:
        """Extrae presupuesto usando regex"""
        text_lower = text.lower()
        
        patterns = [
            r'(\d+)\s*soles',
            r's/?\s*(\d+)',
            r'presupuesto.*?(\d+)',
            r'tengo.*?(\d+)',
            r'cuento\s+con.*?(\d+)',
            r'dispongo.*?(\d+)',
            r'(\d+)\s*(?:mil)?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                budget = int(match.group(1))
                if 'mil' in text_lower and budget < 100:
                    budget *= 1000
                if 100 <= budget <= 50000:
                    return budget
        
        return None
    
    def extract_use_cases(self, text: str) -> List[str]:
        """Extrae casos de uso usando similitud semántica"""
        text_lower = text.lower()
        use_cases = []
        
        # Vectorizar texto de entrada
        text_vector = self.vectorizer.transform([text_lower])
        
        # Calcular similitud con cada template
        similarities = {}
        for use_case, templates_list in self.templates.items():
            templates_text = ' '.join(templates_list)
            template_vector = self.vectorizer.transform([templates_text])
            similarity = cosine_similarity(text_vector, template_vector)[0][0]
            similarities[use_case] = similarity
        
        # Agregar casos de uso con similitud > 0.3
        for use_case, sim in similarities.items():
            if sim > 0.3:
                use_cases.append(use_case)
        
        # También usar keywords como fallback
        if not use_cases:
            if any(kw in text_lower for kw in ['jugar', 'gaming', 'gamer', 'juegos']):
                use_cases.append('gaming')
            if any(kw in text_lower for kw in ['programar', 'programación', 'desarrollo', 'developer']):
                use_cases.append('development')
            if any(kw in text_lower for kw in ['diseño', 'design', 'editar', 'render']):
                use_cases.append('design')
            if any(kw in text_lower for kw in ['oficina', 'office', 'excel', 'word']):
                use_cases.append('office')
        
        return use_cases
    
    def extract_games(self, text: str) -> List[str]:
        """Extrae juegos mencionados"""
        text_lower = text.lower()
        games = []
        
        for game, keywords in self.game_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                games.append(game)
        
        return games
    
    def extract_software(self, text: str) -> List[str]:
        """Extrae software/herramientas mencionadas"""
        text_lower = text.lower()
        software = []
        
        for tool, keywords in self.software_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                software.append(tool)
        
        return software
    
    def extract_performance_level(self, text: str) -> str:
        """Extrae nivel de performance deseado"""
        text_lower = text.lower()
        
        for level in ['high', 'mid', 'budget']:
            keywords = self.performance_patterns[level]
            if any(keyword in text_lower for keyword in keywords):
                return level
        
        games = self.extract_games(text)
        demanding_games = ['cyberpunk', 'cod', 'apex', 'elden ring', 'hogwarts', 'starfield']
        
        if any(game in demanding_games for game in games):
            return 'high'
        elif games:
            return 'mid'
        
        return 'mid'
    
    def infer_priorities(self, use_cases: List[str], games: List[str], 
                        software: List[str]) -> List[str]:
        """Infiere componentes prioritarios según el uso"""
        priorities = []
        
        if 'gaming' in use_cases or games:
            priorities.append('GPU')
            priorities.append('CPU')
            priorities.append('RAM')
        
        if 'development' in use_cases or any(s in ['python', 'java', 'javascript'] for s in software):
            if 'CPU' not in priorities:
                priorities.append('CPU')
            if 'RAM' not in priorities:
                priorities.append('RAM')
            priorities.append('STORAGE')
        
        if 'design' in use_cases or 'video_editing' in use_cases or any(s in ['photoshop', 'blender', 'premiere'] for s in software):
            if 'GPU' not in priorities:
                priorities.append('GPU')
            if 'CPU' not in priorities:
                priorities.append('CPU')
            if 'RAM' not in priorities:
                priorities.append('RAM')
        
        if 'office' in use_cases and not priorities:
            priorities = ['CPU', 'RAM', 'STORAGE']
        
        if not priorities:
            priorities = ['CPU', 'GPU', 'RAM']
        
        return priorities
    
    def map_to_profile(self, parsed_data: Dict) -> str:
        """Mapea datos parseados a un perfil predefinido"""
        use_cases = parsed_data['use_cases']
        budget = parsed_data.get('budget', 1500)
        
        if 'gaming' in use_cases:
            if budget < 1500:
                return 'gamer_budget'
            elif budget < 2500:
                return 'gamer_mid'
            else:
                return 'gamer_high'
        
        if 'development' in use_cases:
            if budget < 1500:
                return 'developer_budget'
            else:
                return 'developer_mid'
        
        if 'design' in use_cases or 'video_editing' in use_cases:
            if budget < 2500:
                return 'designer_mid'
            else:
                return 'designer_high'
        
        if 'office' in use_cases:
            return 'office_budget'
        
        if budget < 1200:
            return 'student_budget'
        
        if budget < 1500:
            return 'gamer_budget'
        elif budget < 2500:
            return 'gamer_mid'
        else:
            return 'gamer_high'
    
    def parse(self, user_message: str) -> Dict:
        """
        Parsea mensaje del usuario usando embeddings
        """
        budget = self.extract_budget(user_message)
        use_cases = self.extract_use_cases(user_message)
        games = self.extract_games(user_message)
        software = self.extract_software(user_message)
        performance_level = self.extract_performance_level(user_message)
        priorities = self.infer_priorities(use_cases, games, software)
        
        parsed_data = {
            'budget': budget,
            'use_cases': use_cases,
            'games': games,
            'software': software,
            'performance_level': performance_level,
            'priorities': priorities,
            'raw_message': user_message
        }
        
        suggested_profile = self.map_to_profile(parsed_data)
        parsed_data['suggested_profile'] = suggested_profile
        
        return parsed_data

