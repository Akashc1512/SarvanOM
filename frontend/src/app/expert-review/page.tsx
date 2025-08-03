"use client";

import { useEffect, useState } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter,
  DialogTrigger 
} from '@/ui/ui/dialog';
import { Button } from '@/ui/ui/button';
import { Textarea } from '@/ui/ui/textarea';
import { Badge } from '@/ui/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { CheckCircle, XCircle, MessageSquare, Clock, AlertCircle } from 'lucide-react';

interface PendingReview {
  id: string;
  query: string;
  answerSnippet: string;
  confidence: number;
  createdAt: string;
  status: 'pending' | 'approved' | 'rejected';
  expertComments?: string;
}

export default function ExpertReviewPage() {
  const [pendingReviews, setPendingReviews] = useState<PendingReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReview, setSelectedReview] = useState<PendingReview | null>(null);
  const [comment, setComment] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  useEffect(() => {
    fetchPendingReviews();
  }, []);

  const fetchPendingReviews = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/factcheck/pending-reviews');
      if (response.ok) {
        const data = await response.json();
        setPendingReviews(data);
      } else {
        console.error('Failed to fetch pending reviews');
        // For demo purposes, create mock data
        setPendingReviews([
          {
            id: '1',
            query: 'What are the main benefits of machine learning in healthcare?',
            answerSnippet: 'Machine learning in healthcare offers improved diagnosis accuracy, personalized treatment plans, and predictive analytics for patient outcomes.',
            confidence: 0.85,
            createdAt: new Date().toISOString(),
            status: 'pending'
          },
          {
            id: '2',
            query: 'How does blockchain technology work?',
            answerSnippet: 'Blockchain is a distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography.',
            confidence: 0.72,
            createdAt: new Date().toISOString(),
            status: 'pending'
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching pending reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitReview = async (reviewId: string, verdict: 'approved' | 'rejected') => {
    try {
      const response = await fetch(`/api/factcheck/review/${reviewId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          verdict,
          comment: comment || undefined
        })
      });

      if (response.ok) {
        // Update local state
        setPendingReviews(prev => 
          prev.map(review => 
            review.id === reviewId 
              ? { ...review, status: verdict, expertComments: comment }
              : review
          )
        );
        
        // Clear comment and close dialog
        setComment('');
        setIsDialogOpen(false);
        
        alert(`Review ${verdict}`);
      } else {
        alert('Failed to submit review');
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Error submitting review');
    }
  };

  const openCommentModal = (review: PendingReview) => {
    setSelectedReview(review);
    setComment(review.expertComments || '');
    setIsDialogOpen(true);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800';
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'rejected':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-600" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Expert Review Dashboard</h1>
        <p className="text-gray-600">Review and validate AI-generated responses for accuracy and quality</p>
      </div>

      {pendingReviews.length === 0 ? (
        <Card>
          <CardContent className="flex items-center justify-center h-32">
            <div className="text-center">
              <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500">No pending reviews at this time</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {pendingReviews.map((review) => (
            <Card key={review.id} className="border-l-4 border-l-blue-500">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(review.status)}
                      <Badge variant={review.status === 'pending' ? 'default' : review.status === 'approved' ? 'default' : 'destructive'}>
                        {review.status.charAt(0).toUpperCase() + review.status.slice(1)}
                      </Badge>
                      <Badge className={getConfidenceColor(review.confidence)}>
                        {Math.round(review.confidence * 100)}% Confidence
                      </Badge>
                    </div>
                    <CardTitle className="text-lg">{review.query}</CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-gray-700 mb-2">AI Response:</h4>
                    <p className="text-gray-600 bg-gray-50 p-3 rounded-md">
                      {review.answerSnippet}
                    </p>
                  </div>
                  
                  {review.expertComments && (
                    <div>
                      <h4 className="font-semibold text-gray-700 mb-2">Expert Comments:</h4>
                      <p className="text-gray-600 bg-blue-50 p-3 rounded-md">
                        {review.expertComments}
                      </p>
                    </div>
                  )}

                  <div className="flex gap-2 pt-4">
                    <Button 
                      onClick={() => submitReview(review.id, 'approved')}
                      className="bg-green-600 hover:bg-green-700"
                      disabled={review.status !== 'pending'}
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Approve
                    </Button>
                    <Button 
                      onClick={() => submitReview(review.id, 'rejected')}
                      variant="destructive"
                      disabled={review.status !== 'pending'}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Reject
                    </Button>
                    <Button 
                      onClick={() => openCommentModal(review)}
                      variant="outline"
                    >
                      <MessageSquare className="h-4 w-4 mr-2" />
                      {review.expertComments ? 'Edit Comment' : 'Add Comment'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Comment Modal */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Add Expert Comment</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label htmlFor="comment" className="text-sm font-medium">
                Your feedback (optional)
              </label>
              <Textarea
                id="comment"
                placeholder="Provide additional context, corrections, or suggestions..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setIsDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button 
              onClick={() => {
                if (selectedReview) {
                  submitReview(selectedReview.id, 'approved');
                }
              }}
              className="bg-green-600 hover:bg-green-700"
            >
              Approve with Comment
            </Button>
            <Button 
              onClick={() => {
                if (selectedReview) {
                  submitReview(selectedReview.id, 'rejected');
                }
              }}
              variant="destructive"
            >
              Reject with Comment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 