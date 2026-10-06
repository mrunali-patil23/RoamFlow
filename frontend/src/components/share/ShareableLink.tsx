import React, { useState } from 'react';
import { TripPlan } from '../../types/trip';

interface ShareableLinkProps {
  tripPlan: TripPlan;
  className?: string;
}

const ShareableLink: React.FC<ShareableLinkProps> = ({ 
  tripPlan, 
  className = "bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
}) => {
  const [shareUrl, setShareUrl] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const generateShareableLink = async () => {
    setIsGenerating(true);
    try {
      // Create a shareable URL by encoding the trip plan data
      const encodedTripData = btoa(JSON.stringify({
        id: tripPlan.id,
        preferences: tripPlan.preferences,
        itinerary: tripPlan.itinerary,
        costBreakdown: tripPlan.costBreakdown,
        budgetStatus: tripPlan.budgetStatus,
        createdAt: tripPlan.createdAt
      }));
      
      const baseUrl = window.location.origin;
      const shareableUrl = `${baseUrl}/shared-trip/${encodedTripData}`;
      setShareUrl(shareableUrl);
    } catch (error) {
      console.error('Error generating shareable link:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  return (
    <div className="space-y-2">
      <button
        onClick={generateShareableLink}
        disabled={isGenerating}
        className={className}
      >
        {isGenerating ? 'Generating Link...' : 'Generate Shareable Link'}
      </button>
      
      {shareUrl && (
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={shareUrl}
              readOnly
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-gray-50"
            />
            <button
              onClick={copyToClipboard}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded text-sm"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <p className="text-sm text-gray-600">
            Share this link with others to let them view your trip plan
          </p>
        </div>
      )}
    </div>
  );
};

export default ShareableLink;