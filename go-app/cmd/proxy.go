package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

// Configuration
const (
	DefaultGoPort     = 50575
	DefaultPythonPort = 59147
	DefaultWebUIPort  = 8000
)

// Request/Response structures
type ProcessingRequest struct {
	Text       string `json:"text"`
	URL        string `json:"url"`
	SourceType string `json:"source_type"`
}

type ProcessingResponse struct {
	Summary    string   `json:"summary"`
	Tags       []string `json:"tags"`
	Analysis   string   `json:"analysis"`
	Status     string   `json:"status"`
	Error      string   `json:"error,omitempty"`
}

type KnowledgeItem struct {
	ID         int      `json:"id"`
	Title      string   `json:"title"`
	Content    string   `json:"content"`
	SourceType string   `json:"source_type"`
	SourceURL  string   `json:"source_url,omitempty"`
	Tags       []string `json:"tags"`
	Summary    string   `json:"summary"`
	Analysis   string   `json:"ai_analysis"`
	CreatedAt  string   `json:"created_at"`
	UpdatedAt  string   `json:"updated_at"`
}

func main() {
	// Get ports from environment or use defaults
	goPort := getEnvInt("GO_PORT", DefaultGoPort)
	pythonPort := getEnvInt("PYTHON_PORT", DefaultPythonPort)
	webUIPort := getEnvInt("WEBUI_PORT", DefaultWebUIPort)

	// Create reverse proxy for Python AI service
	pythonURL, err := url.Parse(fmt.Sprintf("http://localhost:%d", pythonPort))
	if err != nil {
		log.Fatal("Failed to parse Python service URL:", err)
	}
	pythonProxy := httputil.NewSingleHostReverseProxy(pythonURL)

	// Create reverse proxy for Web UI
	webUIURL, err := url.Parse(fmt.Sprintf("http://localhost:%d", webUIPort))
	if err != nil {
		log.Fatal("Failed to parse Web UI URL:", err)
	}
	webUIProxy := httputil.NewSingleHostReverseProxy(webUIURL)

	// Setup routes
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// Enable CORS
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		// Route API requests to Python service
		if strings.HasPrefix(r.URL.Path, "/api/") {
			log.Printf("Proxying API request: %s %s", r.Method, r.URL.Path)
			pythonProxy.ServeHTTP(w, r)
			return
		}

		// Route AI processing requests
		if strings.HasPrefix(r.URL.Path, "/process") {
			handleAIProcessing(w, r, pythonPort)
			return
		}

		// Health check
		if r.URL.Path == "/health" {
			handleHealthCheck(w, r, pythonPort, webUIPort)
			return
		}

		// Serve Web UI for all other requests
		log.Printf("Proxying UI request: %s %s", r.Method, r.URL.Path)
		webUIProxy.ServeHTTP(w, r)
	})

	log.Printf("🚀 KnowledgeGlow Proxy Server starting on port %d", goPort)
	log.Printf("📡 Proxying Python AI Service on port %d", pythonPort)
	log.Printf("🌐 Proxying Web UI on port %d", webUIPort)
	log.Printf("🔗 Access the application at: http://localhost:%d", goPort)

	if err := http.ListenAndServe(fmt.Sprintf(":%d", goPort), nil); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}

func handleAIProcessing(w http.ResponseWriter, r *http.Request, pythonPort int) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Read request body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}

	// Forward to Python AI service
	pythonURL := fmt.Sprintf("http://localhost:%d/api/process", pythonPort)
	resp, err := http.Post(pythonURL, "application/json", bytes.NewBuffer(body))
	if err != nil {
		log.Printf("Error forwarding to Python service: %v", err)
		http.Error(w, "AI service unavailable", http.StatusServiceUnavailable)
		return
	}
	defer resp.Body.Close()

	// Copy response
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}

func handleHealthCheck(w http.ResponseWriter, r *http.Request, pythonPort, webUIPort int) {
	health := map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now().Format(time.RFC3339),
		"services":  map[string]string{},
	}

	// Check Python AI service
	pythonURL := fmt.Sprintf("http://localhost:%d/health", pythonPort)
	if resp, err := http.Get(pythonURL); err == nil && resp.StatusCode == 200 {
		health["services"].(map[string]string)["ai_service"] = "healthy"
		resp.Body.Close()
	} else {
		health["services"].(map[string]string)["ai_service"] = "unhealthy"
	}

	// Check Web UI service
	webUIURL := fmt.Sprintf("http://localhost:%d/health", webUIPort)
	if resp, err := http.Get(webUIURL); err == nil && resp.StatusCode == 200 {
		health["services"].(map[string]string)["web_ui"] = "healthy"
		resp.Body.Close()
	} else {
		health["services"].(map[string]string)["web_ui"] = "unhealthy"
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(health)
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}