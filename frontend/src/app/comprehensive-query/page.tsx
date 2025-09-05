"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/ui/ui/tabs";
import QueryForm from "@/ui/QueryForm";
import { AnswerDisplay } from "@/ui/AnswerDisplay";
import { CitationPanel } from "@/ui/CitationPanel";
import { KnowledgeGraphPanel } from "@/ui/KnowledgeGraphPanel";
import { 
  BookOpen, 
  Search, 
  Brain, 
  MessageSquare, 
  Clock, 
  Network, 
  BarChart3,
  Zap,
  Target,
  Lightbulb,
  TrendingUp,
  Shield,
  Users,
  Globe,
  Database,
  FileText,
  Download,
  Share2,
  Copy,
  ExternalLink,
  Eye,
  EyeOff,
  CheckCircle2,
  XCircle,
  Minus,
  AlertTriangle,
  Info,
  FileDown
} from "lucide-react";
import { type QueryResponse } from "@/services/api";

interface EvidenceItem {
  id: string;
  title: string;
  source: string;
  type: 'academic' | 'news' | 'report' | 'expert';
  confidence: number;
  agreement: 'supporting' | 'contradicting' | 'neutral';
  summary: string;
  date: string;
  url?: string;
  doi?: string;
}

interface SourceItem {
  id: string;
  title: string;
  author: string;
  publication: string;
  year: string;
  type: 'journal' | 'conference' | 'book' | 'report' | 'website';
  doi?: string;
  url?: string;
  citations: number;
  relevance: number;
}

const exampleQueries = [
  {
    title: "Market Research Analysis",
    description: "Comprehensive analysis of market trends, competitors, and opportunities",
    query: "Analyze the current market trends in artificial intelligence, including key players, emerging technologies, market size, and future projections. Include competitive analysis and investment patterns.",
    features: ["Multi-source", "Analytics", "Citations", "Graph"]
  },
  {
    title: "Academic Literature Review",
    description: "In-depth review of academic papers and research findings",
    query: "Conduct a comprehensive literature review on machine learning applications in healthcare, focusing on recent developments, challenges, and future directions. Include peer-reviewed sources and clinical studies.",
    features: ["Academic", "Citations", "Analysis", "Graph"]
  },
  {
    title: "Technical Documentation Research",
    description: "Research technical specifications and implementation details",
    query: "Research the latest developments in React 18 features, including concurrent rendering, automatic batching, and new hooks. Include code examples and migration guides.",
    features: ["Technical", "Code", "Documentation", "Examples"]
  },
  {
    title: "Business Strategy Analysis",
    description: "Strategic analysis of business opportunities and challenges",
    query: "Analyze the business strategy of Tesla in the electric vehicle market, including their competitive advantages, market positioning, challenges, and future outlook. Include financial analysis and industry trends.",
    features: ["Business", "Strategy", "Financial", "Analysis"]
  }
];

export default function ComprehensiveQueryPage() {
  const [currentQuery, setCurrentQuery] = useState<QueryResponse | null>(null);
  const [queryHistory, setQueryHistory] = useState<QueryResponse[]>([]);
  const [showCitations, setShowCitations] = useState(false);
  const [showKnowledgeGraph, setShowKnowledgeGraph] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [activeTab, setActiveTab] = useState("evidence");
  const [selectedEvidence, setSelectedEvidence] = useState<string | null>(null);
  const [exportFormat, setExportFormat] = useState<'pdf' | 'docx' | 'bibtex'>('pdf');

  // Ensure we're on the client side
  useState(() => {
    setIsClient(true);
  });

  const handleQuerySubmit = async (query: QueryResponse) => {
    setCurrentQuery(query);
    setQueryHistory(prev => [query, ...prev.slice(0, 9)]); // Keep last 10 queries
  };

  const handleQueryUpdate = (query: QueryResponse) => {
    setCurrentQuery(query);
  };

  const handleFeedback = (
    rating: number,
    helpful: boolean,
    feedback?: string,
  ) => {
    console.log("Feedback received:", { rating, helpful, feedback });
    // Here you would typically send feedback to your analytics service
  };

  const handleOpenAnalytics = () => {
    if (isClient && typeof window !== "undefined") {
      window.open('/analytics', '_blank');
    }
  };

  const handleExport = (format: 'pdf' | 'docx' | 'bibtex') => {
    console.log(`Exporting as ${format}...`);
    setExportFormat(format);
  };

  const evidenceData: EvidenceItem[] = [
    {
      id: '1',
      title: 'AI Market Growth Analysis 2024',
      source: 'MIT Technology Review',
      type: 'report',
      confidence: 95,
      agreement: 'supporting',
      summary: 'Comprehensive analysis showing 40% year-over-year growth in AI adoption across enterprise sectors.',
      date: '2024-01-15',
      url: 'https://example.com/ai-growth-2024'
    },
    {
      id: '2',
      title: 'Challenges in AI Implementation',
      source: 'Harvard Business Review',
      type: 'academic',
      confidence: 88,
      agreement: 'contradicting',
      summary: 'Research indicating significant barriers to AI adoption including cost, complexity, and talent shortage.',
      date: '2024-02-03',
      doi: '10.1000/example.2'
    },
    {
      id: '3',
      title: 'AI Ethics and Governance Framework',
      source: 'Stanford AI Institute',
      type: 'academic',
      confidence: 92,
      agreement: 'neutral',
      summary: 'Framework for responsible AI development and deployment in enterprise environments.',
      date: '2024-01-28',
      doi: '10.1000/example.3'
    }
  ];

  const sourcesData: SourceItem[] = [
    {
      id: '1',
      title: 'The Future of Artificial Intelligence in Business',
      author: 'Dr. Sarah Chen',
      publication: 'MIT Technology Review',
      year: '2024',
      type: 'journal',
      doi: '10.1000/example.1',
      citations: 45,
      relevance: 95
    },
    {
      id: '2',
      title: 'AI Implementation Challenges in Enterprise',
      author: 'Prof. Michael Rodriguez',
      publication: 'Harvard Business Review',
      year: '2024',
      type: 'journal',
      doi: '10.1000/example.2',
      citations: 32,
      relevance: 88
    },
    {
      id: '3',
      title: 'Ethical AI: A Comprehensive Framework',
      author: 'Dr. Emily Watson',
      publication: 'Stanford AI Institute',
      year: '2024',
      type: 'report',
      url: 'https://example.com/ethical-ai-framework',
      citations: 67,
      relevance: 92
    }
  ];

  const getAgreementIcon = (agreement: string) => {
    switch (agreement) {
      case 'supporting':
        return <CheckCircle2 className="h-4 w-4 text-cosmic-success" />;
      case 'contradicting':
        return <XCircle className="h-4 w-4 text-cosmic-error" />;
      case 'neutral':
        return <Minus className="h-4 w-4 text-cosmic-warning" />;
      default:
        return <Info className="h-4 w-4 text-cosmic-text-tertiary" />;
    }
  };

  const getAgreementColor = (agreement: string) => {
    switch (agreement) {
      case 'supporting':
        return 'border-cosmic-success text-cosmic-success';
      case 'contradicting':
        return 'border-cosmic-error text-cosmic-error';
      case 'neutral':
        return 'border-cosmic-warning text-cosmic-warning';
      default:
        return 'border-cosmic-border-primary text-cosmic-text-tertiary';
    }
  };

  return (
    <div className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4 cosmic-text-primary">
              Comprehensive Research
            </h1>
            <p className="text-lg cosmic-text-secondary max-w-3xl mx-auto">
              Advanced multi-source research with evidence analysis, disagreement detection, and comprehensive bibliography
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-3 space-y-6">
              {/* Research Composer */}
              <Card className="cosmic-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 cosmic-text-primary">
                    <Brain className="h-5 w-5 text-cosmic-primary-500" />
                    Research Composer
                  </CardTitle>
                  <CardDescription className="cosmic-text-secondary">
                    Enter your comprehensive research question for multi-source analysis
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <QueryForm 
                      onSubmit={(query) => {
                        // Handle the query submission
                        console.log('Query submitted:', query);
                      }}
                      placeholder="Enter your comprehensive research question..."
                    />
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <Target className="h-4 w-4 text-cosmic-primary-500" />
                        <span className="text-sm cosmic-text-secondary">Research Depth:</span>
                        <Badge variant="outline" className="border-cosmic-primary-500 text-cosmic-primary-500">
                          Comprehensive
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Zap className="h-4 w-4 text-cosmic-secondary-500" />
                        <span className="text-sm cosmic-text-secondary">Sources:</span>
                        <Badge variant="outline" className="border-cosmic-secondary-500 text-cosmic-secondary-500">
                          Multi-Modal
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Results Tabs */}
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-4 cosmic-bg-secondary border-cosmic-border-primary">
                  <TabsTrigger value="evidence" className="cosmic-text-primary data-[state=active]:cosmic-bg-primary">
                    Evidence
                  </TabsTrigger>
                  <TabsTrigger value="analysis" className="cosmic-text-primary data-[state=active]:cosmic-bg-primary">
                    Analysis
                  </TabsTrigger>
                  <TabsTrigger value="sources" className="cosmic-text-primary data-[state=active]:cosmic-bg-primary">
                    Bibliography
                  </TabsTrigger>
                  <TabsTrigger value="export" className="cosmic-text-primary data-[state=active]:cosmic-bg-primary">
                    Export
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="evidence" className="space-y-4">
                  <Card className="cosmic-card">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="cosmic-text-primary">Evidence Table</CardTitle>
                          <CardDescription className="cosmic-text-secondary">
                            Multi-source evidence with agreement/disagreement analysis
                          </CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            className="cosmic-btn-secondary"
                            onClick={() => setShowCitations(!showCitations)}
                          >
                            {showCitations ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                            {showCitations ? "Hide" : "Show"} Details
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {evidenceData.map((evidence) => (
                          <div 
                            key={evidence.id} 
                            className={`p-4 cosmic-bg-secondary rounded-lg border transition-all duration-200 ${
                              selectedEvidence === evidence.id 
                                ? 'border-cosmic-primary-500 cosmic-glow-primary' 
                                : 'border-cosmic-border-primary hover:border-cosmic-primary-500/50'
                            }`}
                            onClick={() => setSelectedEvidence(selectedEvidence === evidence.id ? null : evidence.id)}
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-3">
                                {getAgreementIcon(evidence.agreement)}
                                <div>
                                  <h4 className="font-medium cosmic-text-primary">{evidence.title}</h4>
                                  <p className="text-sm cosmic-text-secondary">{evidence.source}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge 
                                  variant="outline" 
                                  className={`text-xs ${getAgreementColor(evidence.agreement)}`}
                                >
                                  {evidence.agreement}
                                </Badge>
                                <Badge variant="outline" className="text-xs border-cosmic-border-primary text-cosmic-text-primary">
                                  {evidence.confidence}% confidence
                                </Badge>
                              </div>
                            </div>
                            
                            <p className="text-sm cosmic-text-secondary mb-3">{evidence.summary}</p>
                            
                            {showCitations && (
                              <div className="border-t border-cosmic-border-primary pt-3 mt-3">
                                <div className="flex items-center justify-between text-xs cosmic-text-tertiary">
                                  <div className="flex items-center gap-4">
                                    <span>Type: {evidence.type}</span>
                                    <span>Date: {evidence.date}</span>
                                    {evidence.doi && <span>DOI: {evidence.doi}</span>}
                                  </div>
                                  <div className="flex items-center gap-2">
                                    {evidence.url && (
                                      <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                                        <ExternalLink className="h-3 w-3 mr-1" />
                                        View
                                      </Button>
                                    )}
                                    <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                                      <Copy className="h-3 w-3 mr-1" />
                                      Cite
                                    </Button>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="analysis" className="space-y-4">
                  <Card className="cosmic-card">
                    <CardHeader>
                      <CardTitle className="cosmic-text-primary">Comprehensive Analysis</CardTitle>
                      <CardDescription className="cosmic-text-secondary">
                        Deep analysis with insights, disagreements, and recommendations
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        {/* Agreement Analysis */}
                        <div className="p-4 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary">
                          <h4 className="font-medium cosmic-text-primary mb-3 flex items-center gap-2">
                            <TrendingUp className="h-4 w-4 text-cosmic-primary-500" />
                            Evidence Agreement Analysis
                          </h4>
                          <div className="grid grid-cols-3 gap-4">
                            <div className="text-center">
                              <div className="flex items-center justify-center gap-1 mb-1">
                                <CheckCircle2 className="h-4 w-4 text-cosmic-success" />
                                <span className="text-sm cosmic-text-secondary">Supporting</span>
                              </div>
                              <p className="text-2xl font-bold text-cosmic-success">1</p>
                            </div>
                            <div className="text-center">
                              <div className="flex items-center justify-center gap-1 mb-1">
                                <XCircle className="h-4 w-4 text-cosmic-error" />
                                <span className="text-sm cosmic-text-secondary">Contradicting</span>
                              </div>
                              <p className="text-2xl font-bold text-cosmic-error">1</p>
                            </div>
                            <div className="text-center">
                              <div className="flex items-center justify-center gap-1 mb-1">
                                <Minus className="h-4 w-4 text-cosmic-warning" />
                                <span className="text-sm cosmic-text-secondary">Neutral</span>
                              </div>
                              <p className="text-2xl font-bold text-cosmic-warning">1</p>
                            </div>
                          </div>
                        </div>

                        {/* Key Insights */}
                        <div className="p-4 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary">
                          <h4 className="font-medium cosmic-text-primary mb-3 flex items-center gap-2">
                            <Lightbulb className="h-4 w-4 text-cosmic-secondary-500" />
                            Key Insights
                          </h4>
                          <ul className="space-y-2 text-sm cosmic-text-secondary">
                            <li className="flex items-start gap-2">
                              <CheckCircle2 className="h-4 w-4 text-cosmic-success mt-0.5 flex-shrink-0" />
                              <span>Strong evidence for AI market growth with 40% YoY increase</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <AlertTriangle className="h-4 w-4 text-cosmic-warning mt-0.5 flex-shrink-0" />
                              <span>Implementation challenges remain significant barriers</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <Info className="h-4 w-4 text-cosmic-primary-500 mt-0.5 flex-shrink-0" />
                              <span>Ethical frameworks are becoming standard practice</span>
                            </li>
                          </ul>
                        </div>

                        {/* Recommendations */}
                        <div className="p-4 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary">
                          <h4 className="font-medium cosmic-text-primary mb-3 flex items-center gap-2">
                            <Target className="h-4 w-4 text-cosmic-primary-500" />
                            Recommendations
                          </h4>
                          <ul className="space-y-2 text-sm cosmic-text-secondary">
                            <li className="flex items-start gap-2">
                              <span className="w-2 h-2 bg-cosmic-primary-500 rounded-full mt-2 flex-shrink-0"></span>
                              <span>Focus on addressing implementation barriers through training and support</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <span className="w-2 h-2 bg-cosmic-secondary-500 rounded-full mt-2 flex-shrink-0"></span>
                              <span>Develop comprehensive ethical guidelines before deployment</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <span className="w-2 h-2 bg-cosmic-warning rounded-full mt-2 flex-shrink-0"></span>
                              <span>Monitor market trends and competitor strategies closely</span>
                            </li>
                          </ul>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="sources" className="space-y-4">
                  <Card className="cosmic-card">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="cosmic-text-primary">Bibliography</CardTitle>
                          <CardDescription className="cosmic-text-secondary">
                            Complete list of sources and references with citation metrics
                          </CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            className="cosmic-btn-secondary"
                            onClick={() => handleExport('bibtex')}
                          >
                            <FileText className="h-4 w-4 mr-2" />
                            Export BibTeX
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {sourcesData.map((source) => (
                          <div key={source.id} className="p-4 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary">
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1">
                                <h4 className="font-medium cosmic-text-primary mb-1">{source.title}</h4>
                                <p className="text-sm cosmic-text-secondary mb-2">
                                  {source.author} • {source.publication} • {source.year}
                                </p>
                                <div className="flex items-center gap-4 text-xs cosmic-text-tertiary">
                                  <span className="flex items-center gap-1">
                                    <FileText className="h-3 w-3" />
                                    {source.type}
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Users className="h-3 w-3" />
                                    {source.citations} citations
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Target className="h-3 w-3" />
                                    {source.relevance}% relevance
                                  </span>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                {source.url && (
                                  <Button variant="outline" size="sm" className="cosmic-btn-secondary">
                                    <ExternalLink className="h-3 w-3 mr-1" />
                                    View
                                  </Button>
                                )}
                                <Button variant="outline" size="sm" className="cosmic-btn-secondary">
                                  <Copy className="h-3 w-3 mr-1" />
                                  Cite
                                </Button>
                                <Button variant="outline" size="sm" className="cosmic-btn-secondary">
                                  <Download className="h-3 w-3 mr-1" />
                                  PDF
                                </Button>
                              </div>
                            </div>
                            {source.doi && (
                              <div className="border-t border-cosmic-border-primary pt-2 mt-2">
                                <p className="text-xs cosmic-text-tertiary">
                                  DOI: {source.doi}
                                </p>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="export" className="space-y-4">
                  <Card className="cosmic-card">
                    <CardHeader>
                      <CardTitle className="cosmic-text-primary">Export Research</CardTitle>
                      <CardDescription className="cosmic-text-secondary">
                        Export your comprehensive research in various formats
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        {/* Export Options */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div 
                            className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                              exportFormat === 'pdf' 
                                ? 'border-cosmic-primary-500 cosmic-bg-primary cosmic-glow-primary' 
                                : 'border-cosmic-border-primary cosmic-bg-secondary hover:border-cosmic-primary-500/50'
                            }`}
                            onClick={() => setExportFormat('pdf')}
                          >
                            <div className="flex items-center gap-3 mb-2">
                              <FileText className="h-5 w-5 text-cosmic-primary-500" />
                              <h4 className="font-medium cosmic-text-primary">PDF Report</h4>
                            </div>
                            <p className="text-sm cosmic-text-secondary">
                              Complete research report with all evidence, analysis, and bibliography
                            </p>
                          </div>

                          <div 
                            className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                              exportFormat === 'docx' 
                                ? 'border-cosmic-primary-500 cosmic-bg-primary cosmic-glow-primary' 
                                : 'border-cosmic-border-primary cosmic-bg-secondary hover:border-cosmic-primary-500/50'
                            }`}
                            onClick={() => setExportFormat('docx')}
                          >
                            <div className="flex items-center gap-3 mb-2">
                              <FileText className="h-5 w-5 text-cosmic-secondary-500" />
                              <h4 className="font-medium cosmic-text-primary">Word Document</h4>
                            </div>
                            <p className="text-sm cosmic-text-secondary">
                              Editable document format for further research and collaboration
                            </p>
                          </div>

                          <div 
                            className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                              exportFormat === 'bibtex' 
                                ? 'border-cosmic-primary-500 cosmic-bg-primary cosmic-glow-primary' 
                                : 'border-cosmic-border-primary cosmic-bg-secondary hover:border-cosmic-primary-500/50'
                            }`}
                            onClick={() => setExportFormat('bibtex')}
                          >
                            <div className="flex items-center gap-3 mb-2">
                              <Database className="h-5 w-5 text-cosmic-warning" />
                              <h4 className="font-medium cosmic-text-primary">BibTeX</h4>
                            </div>
                            <p className="text-sm cosmic-text-secondary">
                              Citation database format for academic references
                            </p>
                          </div>
                        </div>

                        {/* Export Actions */}
                        <div className="flex items-center justify-between p-4 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary">
                          <div>
                            <h4 className="font-medium cosmic-text-primary mb-1">
                              Export as {exportFormat.toUpperCase()}
                            </h4>
                            <p className="text-sm cosmic-text-secondary">
                              Includes all evidence, analysis, and bibliography
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              className="cosmic-btn-secondary"
                              onClick={() => handleExport(exportFormat)}
                            >
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </Button>
                            <Button
                              variant="outline"
                              className="cosmic-btn-secondary"
                              onClick={() => console.log('Share research...')}
                            >
                              <Share2 className="h-4 w-4 mr-2" />
                              Share
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Research Status */}
              <Card className="cosmic-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 cosmic-text-primary">
                    <Clock className="h-5 w-5 text-cosmic-primary-500" />
                    Research Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm cosmic-text-secondary">Sources Analyzed</span>
                      <span className="text-sm font-medium cosmic-text-primary">3/5</span>
                    </div>
                    <div className="w-full cosmic-bg-secondary rounded-full h-2">
                      <div className="bg-cosmic-primary-500 h-2 rounded-full" style={{ width: "60%" }}></div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm cosmic-text-secondary">Evidence Quality</span>
                      <span className="text-sm font-medium text-cosmic-success">92%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm cosmic-text-secondary">Agreement Score</span>
                      <span className="text-sm font-medium text-cosmic-warning">67%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm cosmic-text-secondary">Time Elapsed</span>
                      <span className="text-sm font-medium cosmic-text-primary">1m 23s</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Example Queries */}
              <Card className="cosmic-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 cosmic-text-primary">
                    <BookOpen className="h-5 w-5 text-cosmic-primary-500" />
                    Example Queries
                  </CardTitle>
                  <CardDescription className="cosmic-text-secondary">
                    Try these comprehensive research examples
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {exampleQueries.map((example, index) => (
                      <div key={index} className="cosmic-card border-cosmic-border-primary rounded-lg p-4">
                        <h4 className="font-medium text-sm mb-2 cosmic-text-primary">{example.title}</h4>
                        <p className="text-xs cosmic-text-tertiary mb-3">{example.description}</p>
                        <div className="flex flex-wrap gap-1 mb-3">
                          {example.features.map((feature, featureIndex) => (
                            <Badge key={featureIndex} variant="outline" className="text-xs border-cosmic-border-primary text-cosmic-text-primary">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full cosmic-btn-secondary"
                          onClick={() => {
                            // This would trigger the query form with the example
                            console.log("Example query:", example.query);
                          }}
                        >
                          Try This Query
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Quick Actions */}
              <Card className="cosmic-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 cosmic-text-primary">
                    <Zap className="h-5 w-5 text-cosmic-secondary-500" />
                    Quick Actions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start cosmic-btn-secondary"
                      onClick={() => setShowKnowledgeGraph(!showKnowledgeGraph)}
                    >
                      <Network className="h-4 w-4 mr-2" />
                      {showKnowledgeGraph ? "Hide" : "Show"} Knowledge Graph
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start cosmic-btn-secondary"
                      onClick={handleOpenAnalytics}
                    >
                      <BarChart3 className="h-4 w-4 mr-2" />
                      View Analytics
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start cosmic-btn-secondary"
                      onClick={() => console.log('Save research...')}
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      Save Research
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Research Tips */}
              <Card className="cosmic-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 cosmic-text-primary">
                    <Lightbulb className="h-5 w-5 text-cosmic-warning" />
                    Research Tips
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm cosmic-text-secondary">
                    <div className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-cosmic-success mt-0.5 flex-shrink-0" />
                      <span>Look for conflicting evidence to ensure balanced analysis</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <Target className="h-4 w-4 text-cosmic-primary-500 mt-0.5 flex-shrink-0" />
                      <span>Focus on recent, high-quality sources for accuracy</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <Globe className="h-4 w-4 text-cosmic-secondary-500 mt-0.5 flex-shrink-0" />
                      <span>Include diverse perspectives and methodologies</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

