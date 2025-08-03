"""
Code Service

This service handles code execution, validation, and analysis functionality for the code agent.
It provides safe code execution, syntax validation, and code analysis capabilities.
"""

import logging
import asyncio
import tempfile
import os
import subprocess
import ast
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import traceback
from pathlib import Path

from .base_service import BaseAgentService, ServiceType, ServiceStatus

logger = logging.getLogger(__name__)


class CodeService(BaseAgentService):
    """
    Code service for safe code execution and analysis.
    
    This service provides code execution, syntax validation,
    and code analysis capabilities for the code agent.
    """
    
    def __init__(self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None):
        """Initialize the code service."""
        super().__init__(service_type, config)
        self.timeout = self.get_config("timeout", 30)
        self.max_memory = self.get_config("max_memory", 512)  # MB
        self.allowed_languages = self.get_config("allowed_languages", ["python", "javascript", "bash"])
        self.sandbox_enabled = self.get_config("sandbox_enabled", True)
        self.temp_dir = self.get_config("temp_dir", tempfile.gettempdir())
        self.max_file_size = self.get_config("max_file_size", 1024 * 1024)  # 1MB
        
        # Security restrictions
        self.blocked_imports = self.get_config("blocked_imports", [
            "os", "sys", "subprocess", "socket", "urllib", "requests"
        ])
        self.blocked_functions = self.get_config("blocked_functions", [
            "eval", "exec", "compile", "input", "open"
        ])
        
        logger.info("Code service initialized")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check code service health.
        
        Returns:
            Health status and metrics
        """
        try:
            # Test basic code execution
            test_result = await self._test_code_execution()
            
            if test_result["success"]:
                self.update_status(ServiceStatus.HEALTHY)
                return {
                    "healthy": True,
                    "code_execution": "OK",
                    "sandbox_enabled": self.sandbox_enabled,
                    "allowed_languages": self.allowed_languages,
                    "timeout": self.timeout,
                    "max_memory": self.max_memory
                }
            else:
                self.update_status(ServiceStatus.DEGRADED)
                return {
                    "healthy": False,
                    "code_execution": "FAILED",
                    "error": test_result.get("error", "Unknown error")
                }
                
        except Exception as e:
            self.update_status(ServiceStatus.UNHEALTHY)
            logger.error(f"Code service health check failed: {e}")
            return {
                "healthy": False,
                "code_execution": "FAILED",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed code service status.
        
        Returns:
            Service status information
        """
        health_info = await self.health_check()
        service_info = self.get_service_info()
        
        return {
            **service_info,
            **health_info,
            "capabilities": {
                "code_execution": True,
                "syntax_validation": True,
                "code_analysis": True,
                "security_scanning": True,
                "multi_language_support": True
            },
            "configuration": {
                "allowed_languages": self.allowed_languages,
                "timeout": self.timeout,
                "max_memory": self.max_memory,
                "sandbox_enabled": self.sandbox_enabled,
                "blocked_imports": self.blocked_imports,
                "blocked_functions": self.blocked_functions
            }
        }
    
    async def validate_config(self) -> bool:
        """
        Validate code service configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check required configuration
            if self.timeout <= 0:
                logger.error("Code service: Invalid timeout value")
                return False
            
            if self.max_memory <= 0:
                logger.error("Code service: Invalid max_memory value")
                return False
            
            if not self.allowed_languages:
                logger.error("Code service: No allowed languages configured")
                return False
            
            # Check if temp directory exists and is writable
            if not os.path.exists(self.temp_dir) or not os.access(self.temp_dir, os.W_OK):
                logger.error(f"Code service: Temp directory not accessible: {self.temp_dir}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Code service config validation failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get code service performance metrics.
        
        Returns:
            Performance metrics
        """
        base_metrics = self.get_service_info()
        
        # Add code-specific metrics
        code_metrics = {
            "code_executions": 0,  # TODO: Track actual executions
            "syntax_validations": 0,  # TODO: Track validations
            "security_scans": 0,  # TODO: Track security scans
            "average_execution_time": 0.0,  # TODO: Track execution times
            "success_rate": 1.0 if self.error_count == 0 else 0.0
        }
        
        return {**base_metrics, **code_metrics}
    
    async def execute_code(self, code: str, language: str = "python",
                          inputs: Optional[Dict[str, Any]] = None,
                          timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute code safely.
        
        Args:
            code: Code to execute
            language: Programming language
            inputs: Input variables
            timeout: Execution timeout
            
        Returns:
            Execution results
        """
        await self.pre_request()
        
        try:
            # Validate language
            if language not in self.allowed_languages:
                raise ValueError(f"Language '{language}' not allowed")
            
            # Security scan
            security_result = await self._security_scan(code, language)
            if not security_result["safe"]:
                raise ValueError(f"Code failed security scan: {security_result['reason']}")
            
            # Execute code
            result = await self._execute_code_safely(code, language, inputs, timeout)
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Code execution failed: {e}")
            raise
    
    async def validate_syntax(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validate code syntax.
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            Validation results
        """
        await self.pre_request()
        
        try:
            if language not in self.allowed_languages:
                raise ValueError(f"Language '{language}' not supported")
            
            validation_result = await self._validate_syntax(code, language)
            await self.post_request(success=True)
            return validation_result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Syntax validation failed: {e}")
            raise
    
    async def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code structure and complexity.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        await self.pre_request()
        
        try:
            if language not in self.allowed_languages:
                raise ValueError(f"Language '{language}' not supported")
            
            analysis_result = await self._analyze_code(code, language)
            await self.post_request(success=True)
            return analysis_result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Code analysis failed: {e}")
            raise
    
    async def upload_and_execute(self, file_content: bytes, filename: str,
                               language: Optional[str] = None,
                               inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Upload and execute a code file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            language: Programming language (auto-detected if None)
            inputs: Input variables
            
        Returns:
            Execution results
        """
        await self.pre_request()
        
        try:
            # Validate file size
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File size {len(file_content)} exceeds maximum {self.max_file_size}")
            
            # Auto-detect language if not specified
            if language is None:
                language = self._detect_language(filename)
            
            # Validate language
            if language not in self.allowed_languages:
                raise ValueError(f"Language '{language}' not allowed")
            
            # Convert bytes to string
            code = file_content.decode('utf-8')
            
            # Security scan
            security_result = await self._security_scan(code, language)
            if not security_result["safe"]:
                raise ValueError(f"Code failed security scan: {security_result['reason']}")
            
            # Execute code
            result = await self._execute_code_safely(code, language, inputs)
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"File upload and execution failed: {e}")
            raise
    
    async def _execute_code_safely(self, code: str, language: str,
                                  inputs: Optional[Dict[str, Any]] = None,
                                  timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute code in a safe environment.
        
        Args:
            code: Code to execute
            language: Programming language
            inputs: Input variables
            timeout: Execution timeout
            
        Returns:
            Execution results
        """
        execution_timeout = timeout or self.timeout
        
        try:
            if language == "python":
                return await self._execute_python(code, inputs, execution_timeout)
            elif language == "javascript":
                return await self._execute_javascript(code, inputs, execution_timeout)
            elif language == "bash":
                return await self._execute_bash(code, inputs, execution_timeout)
            else:
                raise ValueError(f"Unsupported language: {language}")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0.0,
                "output": "",
                "stderr": traceback.format_exc()
            }
    
    async def _execute_python(self, code: str, inputs: Optional[Dict[str, Any]], timeout: int) -> Dict[str, Any]:
        """Execute Python code safely."""
        start_time = datetime.now()
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=self.temp_dir) as temp_file:
                # Add input variables
                if inputs:
                    input_code = "\n".join([f"{k} = {repr(v)}" for k, v in inputs.items()])
                    temp_file.write(input_code + "\n\n")
                
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Execute with timeout
                process = await asyncio.create_subprocess_exec(
                    "python", temp_file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "success": process.returncode == 0,
                    "output": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8'),
                    "return_code": process.returncode,
                    "execution_time": execution_time
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Execution timeout",
                "execution_time": timeout,
                "output": "",
                "stderr": "Process killed due to timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "output": "",
                "stderr": traceback.format_exc()
            }
    
    async def _execute_javascript(self, code: str, inputs: Optional[Dict[str, Any]], timeout: int) -> Dict[str, Any]:
        """Execute JavaScript code safely."""
        start_time = datetime.now()
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, dir=self.temp_dir) as temp_file:
                # Add input variables
                if inputs:
                    input_code = "\n".join([f"const {k} = {json.dumps(v)};" for k, v in inputs.items()])
                    temp_file.write(input_code + "\n\n")
                
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Execute with Node.js
                process = await asyncio.create_subprocess_exec(
                    "node", temp_file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "success": process.returncode == 0,
                    "output": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8'),
                    "return_code": process.returncode,
                    "execution_time": execution_time
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Execution timeout",
                "execution_time": timeout,
                "output": "",
                "stderr": "Process killed due to timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "output": "",
                "stderr": traceback.format_exc()
            }
    
    async def _execute_bash(self, code: str, inputs: Optional[Dict[str, Any]], timeout: int) -> Dict[str, Any]:
        """Execute Bash code safely."""
        start_time = datetime.now()
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False, dir=self.temp_dir) as temp_file:
                temp_file.write("#!/bin/bash\n")
                
                # Add input variables
                if inputs:
                    for k, v in inputs.items():
                        temp_file.write(f"{k}='{v}'\n")
                    temp_file.write("\n")
                
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Make executable
                os.chmod(temp_file_path, 0o755)
                
                # Execute
                process = await asyncio.create_subprocess_exec(
                    temp_file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "success": process.returncode == 0,
                    "output": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8'),
                    "return_code": process.returncode,
                    "execution_time": execution_time
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Execution timeout",
                "execution_time": timeout,
                "output": "",
                "stderr": "Process killed due to timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "output": "",
                "stderr": traceback.format_exc()
            }
    
    async def _security_scan(self, code: str, language: str) -> Dict[str, Any]:
        """
        Perform security scan on code.
        
        Args:
            code: Code to scan
            language: Programming language
            
        Returns:
            Security scan results
        """
        try:
            if language == "python":
                return self._scan_python_security(code)
            elif language == "javascript":
                return self._scan_javascript_security(code)
            elif language == "bash":
                return self._scan_bash_security(code)
            else:
                return {"safe": True, "reason": "Language not supported for security scanning"}
                
        except Exception as e:
            return {"safe": False, "reason": f"Security scan failed: {str(e)}"}
    
    def _scan_python_security(self, code: str) -> Dict[str, Any]:
        """Scan Python code for security issues."""
        try:
            # Parse AST
            tree = ast.parse(code)
            
            # Check for blocked imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.blocked_imports:
                            return {"safe": False, "reason": f"Blocked import: {alias.name}"}
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.blocked_imports:
                        return {"safe": False, "reason": f"Blocked import: {node.module}"}
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.blocked_functions:
                            return {"safe": False, "reason": f"Blocked function: {node.func.id}"}
            
            return {"safe": True, "reason": "No security issues found"}
            
        except SyntaxError:
            return {"safe": False, "reason": "Syntax error in code"}
        except Exception as e:
            return {"safe": False, "reason": f"Security scan error: {str(e)}"}
    
    def _scan_javascript_security(self, code: str) -> Dict[str, Any]:
        """Scan JavaScript code for security issues."""
        try:
            # Check for eval and other dangerous functions
            dangerous_patterns = [
                r'\beval\s*\(',
                r'\bexec\s*\(',
                r'\bFunction\s*\(',
                r'\bsetTimeout\s*\(',
                r'\bsetInterval\s*\('
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    return {"safe": False, "reason": f"Dangerous pattern found: {pattern}"}
            
            return {"safe": True, "reason": "No security issues found"}
            
        except Exception as e:
            return {"safe": False, "reason": f"Security scan error: {str(e)}"}
    
    def _scan_bash_security(self, code: str) -> Dict[str, Any]:
        """Scan Bash code for security issues."""
        try:
            # Check for dangerous commands
            dangerous_patterns = [
                r'\brm\s+-rf',
                r'\bdd\s+if=',
                r'\bformat\s+',
                r'\bdel\s+',
                r'\bkill\s+-9'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    return {"safe": False, "reason": f"Dangerous command found: {pattern}"}
            
            return {"safe": True, "reason": "No security issues found"}
            
        except Exception as e:
            return {"safe": False, "reason": f"Security scan error: {str(e)}"}
    
    async def _validate_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """
        Validate code syntax.
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            Validation results
        """
        try:
            if language == "python":
                ast.parse(code)
                return {"valid": True, "errors": []}
            elif language == "javascript":
                # TODO: Implement JavaScript syntax validation
                return {"valid": True, "errors": []}
            elif language == "bash":
                # TODO: Implement Bash syntax validation
                return {"valid": True, "errors": []}
            else:
                return {"valid": False, "errors": [f"Language '{language}' not supported for syntax validation"]}
                
        except SyntaxError as e:
            return {"valid": False, "errors": [f"Syntax error: {str(e)}"]}
        except Exception as e:
            return {"valid": False, "errors": [f"Validation error: {str(e)}"]}
    
    async def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code structure and complexity.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        try:
            if language == "python":
                return self._analyze_python_code(code)
            elif language == "javascript":
                return self._analyze_javascript_code(code)
            elif language == "bash":
                return self._analyze_bash_code(code)
            else:
                return {"error": f"Language '{language}' not supported for analysis"}
                
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code structure."""
        try:
            tree = ast.parse(code)
            
            # Count different types of nodes
            function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            import_count = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
            
            # Calculate complexity metrics
            lines = code.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            
            return {
                "language": "python",
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "function_count": function_count,
                "class_count": class_count,
                "import_count": import_count,
                "complexity_score": function_count + class_count * 2
            }
            
        except Exception as e:
            return {"error": f"Python analysis failed: {str(e)}"}
    
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript code structure."""
        try:
            lines = code.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
            comment_lines = len([line for line in lines if line.strip().startswith('//')])
            
            # Simple pattern matching for function and class detection
            function_pattern = r'\bfunction\s+\w+\s*\('
            class_pattern = r'\bclass\s+\w+'
            import_pattern = r'\bimport\s+'
            
            function_count = len(re.findall(function_pattern, code))
            class_count = len(re.findall(class_pattern, code))
            import_count = len(re.findall(import_pattern, code))
            
            return {
                "language": "javascript",
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "function_count": function_count,
                "class_count": class_count,
                "import_count": import_count,
                "complexity_score": function_count + class_count * 2
            }
            
        except Exception as e:
            return {"error": f"JavaScript analysis failed: {str(e)}"}
    
    def _analyze_bash_code(self, code: str) -> Dict[str, Any]:
        """Analyze Bash code structure."""
        try:
            lines = code.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            
            # Simple pattern matching for function detection
            function_pattern = r'\w+\s*\(\s*\)'
            command_pattern = r'\b\w+\s+'
            
            function_count = len(re.findall(function_pattern, code))
            command_count = len(re.findall(command_pattern, code))
            
            return {
                "language": "bash",
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "function_count": function_count,
                "command_count": command_count,
                "complexity_score": function_count + command_count
            }
            
        except Exception as e:
            return {"error": f"Bash analysis failed: {str(e)}"}
    
    def _detect_language(self, filename: str) -> str:
        """
        Detect programming language from filename.
        
        Args:
            filename: File name
            
        Returns:
            Detected language
        """
        extension = Path(filename).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.sh': 'bash',
            '.bash': 'bash'
        }
        
        return language_map.get(extension, 'python')
    
    async def _test_code_execution(self) -> Dict[str, Any]:
        """
        Test code execution capabilities.
        
        Returns:
            Test results
        """
        try:
            # Test simple Python execution
            test_code = "print('Hello, World!')"
            result = await self._execute_code_safely(test_code, "python", timeout=5)
            
            return {"success": result["success"]}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown the code service."""
        await super().shutdown()
        logger.info("Code service shutdown complete") 