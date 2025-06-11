"""
Auth0 Configuration and Authentication Module

This module handles Auth0 authentication, GitHub OAuth integration,
and user session management for the multi-agent system.
"""

import os
import jwt
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import wraps
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import aiohttp


class Auth0Config:
    """Auth0 configuration and client"""
    
    def __init__(self):
        self.domain = os.getenv('AUTH0_DOMAIN')
        self.client_id = os.getenv('AUTH0_CLIENT_ID')
        self.client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        self.audience = os.getenv('AUTH0_AUDIENCE', f'https://{self.domain}/api/v2/')
        self.algorithms = ['RS256']
        
        self.is_configured = all([self.domain, self.client_id, self.client_secret])
        
        if not self.is_configured:
            print("⚠️ Auth0 configuration not found. Authentication will be disabled.")
            # No levantamos error, solo configuramos las URLs como None
            self.jwks_url = None
            self.token_url = None
            self.userinfo_url = None
            return
        
        self.jwks_url = f'https://{self.domain}/.well-known/jwks.json'
        self.token_url = f'https://{self.domain}/oauth/token'
        self.userinfo_url = f'https://{self.domain}/userinfo'
        
        # Cache for JWKS
        self._jwks_cache = None
        self._jwks_cache_time = None
        self._cache_duration = timedelta(hours=1)
    
    async def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Auth0"""
        
        # Check cache
        if (self._jwks_cache and self._jwks_cache_time and 
            datetime.now() - self._jwks_cache_time < self._cache_duration):
            return self._jwks_cache
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.jwks_url) as response:
                    if response.status == 200:
                        jwks = await response.json()
                        self._jwks_cache = jwks
                        self._jwks_cache_time = datetime.now()
                        return jwks
                    else:
                        raise HTTPException(status_code=500, detail="Failed to fetch JWKS")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"JWKS fetch error: {str(e)}")
    
    def get_rsa_key(self, token: str) -> Dict[str, Any]:
        """Get RSA key for token verification"""
        
        try:
            unverified_header = jwt.get_unverified_header(token)
            jwks = asyncio.run(self.get_jwks())
            
            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    break
            
            if not rsa_key:
                raise HTTPException(status_code=401, detail="Unable to find appropriate key")
            
            return rsa_key
            
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token verification error: {str(e)}")


class GitHubIntegration:
    """GitHub OAuth and API integration"""
    
    def __init__(self, auth0_config: Auth0Config):
        self.auth0_config = auth0_config
        self.github_api_base = "https://api.github.com"
    
    async def get_github_token(self, user_id: str) -> Optional[str]:
        """Get GitHub access token for user from Auth0"""
        
        try:
            # Get management API token
            mgmt_token = await self.get_management_token()
            
            # Get user's GitHub connection
            headers = {
                'Authorization': f'Bearer {mgmt_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"https://{self.auth0_config.domain}/api/v2/users/{user_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        
                        # Look for GitHub identity
                        for identity in user_data.get('identities', []):
                            if identity.get('provider') == 'github':
                                return identity.get('access_token')
                        
                        return None
                    else:
                        print(f"Failed to get user data: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error getting GitHub token: {e}")
            return None
    
    async def get_management_token(self) -> str:
        """Get Auth0 Management API token"""
        
        try:
            data = {
                'client_id': self.auth0_config.client_id,
                'client_secret': self.auth0_config.client_secret,
                'audience': f'https://{self.auth0_config.domain}/api/v2/',
                'grant_type': 'client_credentials'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.auth0_config.token_url, json=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        return token_data['access_token']
                    else:
                        raise HTTPException(status_code=500, detail="Failed to get management token")
                        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Management token error: {str(e)}")
    
    async def get_user_repositories(self, github_token: str) -> List[Dict[str, Any]]:
        """Get user's GitHub repositories"""
        
        try:
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            repositories = []
            page = 1
            per_page = 30
            
            async with aiohttp.ClientSession() as session:
                while True:
                    url = f"{self.github_api_base}/user/repos"
                    params = {
                        'page': page,
                        'per_page': per_page,
                        'sort': 'updated',
                        'type': 'all'
                    }
                    
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            repos = await response.json()
                            if not repos:
                                break
                            
                            for repo in repos:
                                repositories.append({
                                    'id': repo['id'],
                                    'name': repo['name'],
                                    'full_name': repo['full_name'],
                                    'description': repo['description'],
                                    'private': repo['private'],
                                    'html_url': repo['html_url'],
                                    'clone_url': repo['clone_url'],
                                    'language': repo['language'],
                                    'updated_at': repo['updated_at'],
                                    'size': repo['size'],
                                    'stargazers_count': repo['stargazers_count'],
                                    'forks_count': repo['forks_count']
                                })
                            
                            page += 1
                            if len(repos) < per_page:
                                break
                        else:
                            print(f"Failed to fetch repositories: {response.status}")
                            break
            
            return repositories
            
        except Exception as e:
            print(f"Error fetching repositories: {e}")
            return []
    
    async def get_repository_content(self, github_token: str, repo_full_name: str, path: str = "") -> Dict[str, Any]:
        """Get repository content and structure"""
        
        try:
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f"{self.github_api_base}/repos/{repo_full_name}/contents/{path}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.json()
                        return {
                            'success': True,
                            'content': content
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_repository_structure(self, github_token: str, repo_full_name: str) -> Dict[str, Any]:
        """Analyze repository structure and provide insights"""
        
        try:
            # Get repository info
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            repo_url = f"{self.github_api_base}/repos/{repo_full_name}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(repo_url, headers=headers) as response:
                    if response.status != 200:
                        return {'success': False, 'error': 'Repository not found'}
                    
                    repo_info = await response.json()
                
                # Get repository contents
                content_result = await self.get_repository_content(github_token, repo_full_name)
                if not content_result['success']:
                    return content_result
                
                # Analyze structure
                analysis = {
                    'repository_info': {
                        'name': repo_info['name'],
                        'description': repo_info['description'],
                        'language': repo_info['language'],
                        'size': repo_info['size'],
                        'stars': repo_info['stargazers_count'],
                        'forks': repo_info['forks_count'],
                        'created_at': repo_info['created_at'],
                        'updated_at': repo_info['updated_at']
                    },
                    'structure_analysis': self._analyze_file_structure(content_result['content']),
                    'project_type': self._detect_project_type(content_result['content']),
                    'technologies': self._detect_technologies(content_result['content']),
                    'complexity_score': self._calculate_complexity_score(repo_info, content_result['content'])
                }
                
                return {
                    'success': True,
                    'analysis': analysis
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_file_structure(self, contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze file structure of repository"""
        
        file_types = {}
        directories = []
        files = []
        
        for item in contents:
            if item['type'] == 'dir':
                directories.append(item['name'])
            else:
                files.append(item['name'])
                
                # Count file types
                if '.' in item['name']:
                    ext = item['name'].split('.')[-1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            'total_files': len(files),
            'total_directories': len(directories),
            'file_types': file_types,
            'directories': directories,
            'files': files
        }
    
    def _detect_project_type(self, contents: List[Dict[str, Any]]) -> str:
        """Detect project type based on files"""
        
        files = [item['name'].lower() for item in contents if item['type'] == 'file']
        
        # Check for common project indicators
        if 'package.json' in files:
            return 'Node.js/JavaScript'
        elif 'requirements.txt' in files or 'setup.py' in files or 'pyproject.toml' in files:
            return 'Python'
        elif 'cargo.toml' in files:
            return 'Rust'
        elif 'go.mod' in files:
            return 'Go'
        elif 'pom.xml' in files or 'build.gradle' in files:
            return 'Java'
        elif 'composer.json' in files:
            return 'PHP'
        elif 'gemfile' in files:
            return 'Ruby'
        elif any(f.endswith('.csproj') for f in files):
            return 'C#/.NET'
        else:
            return 'Unknown'
    
    def _detect_technologies(self, contents: List[Dict[str, Any]]) -> List[str]:
        """Detect technologies used in the project"""
        
        technologies = []
        files = [item['name'].lower() for item in contents if item['type'] == 'file']
        
        # Framework/technology detection
        if 'dockerfile' in files:
            technologies.append('Docker')
        if 'docker-compose.yml' in files or 'docker-compose.yaml' in files:
            technologies.append('Docker Compose')
        if '.github' in [item['name'] for item in contents if item['type'] == 'dir']:
            technologies.append('GitHub Actions')
        if 'readme.md' in files:
            technologies.append('Documentation')
        if any(f.startswith('.env') for f in files):
            technologies.append('Environment Configuration')
        
        return technologies
    
    def _calculate_complexity_score(self, repo_info: Dict[str, Any], contents: List[Dict[str, Any]]) -> int:
        """Calculate project complexity score (1-10)"""
        
        score = 1
        
        # Size factor
        size_kb = repo_info.get('size', 0)
        if size_kb > 10000:  # > 10MB
            score += 3
        elif size_kb > 1000:  # > 1MB
            score += 2
        elif size_kb > 100:   # > 100KB
            score += 1
        
        # File count factor
        file_count = len([item for item in contents if item['type'] == 'file'])
        if file_count > 50:
            score += 2
        elif file_count > 20:
            score += 1
        
        # Directory structure factor
        dir_count = len([item for item in contents if item['type'] == 'dir'])
        if dir_count > 10:
            score += 2
        elif dir_count > 5:
            score += 1
        
        # Popularity factor
        stars = repo_info.get('stargazers_count', 0)
        if stars > 1000:
            score += 1
        
        return min(score, 10)


# Global instances
auth0_config = Auth0Config()
github_integration = GitHubIntegration(auth0_config)
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token and return user info"""
    
    token = credentials.credentials
    
    try:
        # Get RSA key
        rsa_key = auth0_config.get_rsa_key(token)
        
        # Verify token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=auth0_config.algorithms,
            audience=auth0_config.audience,
            issuer=f'https://{auth0_config.domain}/'
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # This will be handled by FastAPI dependency injection
        return await f(*args, **kwargs)
    return decorated_function


async def get_current_user(token_payload: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """Get current user information"""
    
    user_id = token_payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
    
    return {
        'user_id': user_id,
        'email': token_payload.get('email'),
        'name': token_payload.get('name'),
        'picture': token_payload.get('picture'),
        'permissions': token_payload.get('permissions', [])
    }


async def get_user_github_token(user: Dict[str, Any] = Depends(get_current_user)) -> Optional[str]:
    """Get GitHub token for current user"""
    
    return await github_integration.get_github_token(user['user_id'])
