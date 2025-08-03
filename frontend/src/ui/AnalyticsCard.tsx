interface AnalyticsCardProps {
  title: string;
  value: string | number;
  icon?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

export function AnalyticsCard({ 
  title, 
  value, 
  icon, 
  trend, 
  trendValue 
}: AnalyticsCardProps) {
  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return '↗️';
      case 'down':
        return '↘️';
      default:
        return '→';
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {icon && (
            <span className="text-2xl" role="img" aria-label={title}>
              {icon}
            </span>
          )}
          <div>
            <h3 className="text-sm font-medium text-gray-600">{title}</h3>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
        </div>
        
        {trend && trendValue && (
          <div className={`flex items-center space-x-1 text-sm font-medium ${getTrendColor()}`}>
            <span>{getTrendIcon()}</span>
            <span>{trendValue}</span>
          </div>
        )}
      </div>
    </div>
  );
} 