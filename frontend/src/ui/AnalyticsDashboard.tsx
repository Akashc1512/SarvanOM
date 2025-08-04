"use client";

import { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { Line, Bar, Doughnut } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface AnalyticsChartProps {
  queriesOverTime: Array<{ date: string; count: number }>;
  validationsOverTime: Array<{ date: string; count: number }>;
  topTopics: Array<{ topic: string; count: number }>;
  isLoading?: boolean;
}

export function AnalyticsDashboard({
  queriesOverTime,
  validationsOverTime,
  topTopics,
  isLoading = false,
}: AnalyticsChartProps) {
  const [chartData, setChartData] = useState({
    queries: null,
    validations: null,
    topics: null,
  });

  useEffect(() => {
    if (isLoading) return;

    // Prepare queries over time data
    const queriesData = {
      labels: queriesOverTime.map(item => new Date(item.date).toLocaleDateString()),
      datasets: [
        {
          label: "Queries",
          data: queriesOverTime.map(item => item.count),
          borderColor: "rgb(59, 130, 246)",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    };

    // Prepare validations over time data
    const validationsData = {
      labels: validationsOverTime.map(item => new Date(item.date).toLocaleDateString()),
      datasets: [
        {
          label: "Expert Validations",
          data: validationsOverTime.map(item => item.count),
          backgroundColor: "rgba(34, 197, 94, 0.8)",
          borderColor: "rgb(34, 197, 94)",
          borderWidth: 1,
        },
      ],
    };

    // Prepare top topics data
    const topicsData = {
      labels: topTopics.slice(0, 8).map(item => item.topic),
      datasets: [
        {
          label: "Query Count",
          data: topTopics.slice(0, 8).map(item => item.count),
          backgroundColor: [
            "rgba(59, 130, 246, 0.8)",
            "rgba(16, 185, 129, 0.8)",
            "rgba(245, 158, 11, 0.8)",
            "rgba(239, 68, 68, 0.8)",
            "rgba(139, 92, 246, 0.8)",
            "rgba(236, 72, 153, 0.8)",
            "rgba(14, 165, 233, 0.8)",
            "rgba(34, 197, 94, 0.8)",
          ],
          borderColor: [
            "rgb(59, 130, 246)",
            "rgb(16, 185, 129)",
            "rgb(245, 158, 11)",
            "rgb(239, 68, 68)",
            "rgb(139, 92, 246)",
            "rgb(236, 72, 153)",
            "rgb(14, 165, 233)",
            "rgb(34, 197, 94)",
          ],
          borderWidth: 2,
        },
      ],
    };

    setChartData({
      queries: queriesData,
      validations: validationsData,
      topics: topicsData,
    });
  }, [queriesOverTime, validationsOverTime, topTopics, isLoading]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
      },
      tooltip: {
        mode: "index" as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  const lineChartOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      legend: {
        display: false,
      },
    },
    interaction: {
      mode: "index" as const,
      intersect: false,
    },
  };

  const barChartOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      legend: {
        display: false,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom" as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || "";
            const value = context.parsed;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-[300px] bg-gray-100 rounded-lg animate-pulse" />
          <div className="h-[300px] bg-gray-100 rounded-lg animate-pulse" />
        </div>
        <div className="h-[300px] bg-gray-100 rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Line and Bar Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Queries Over Time - Line Chart */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">Queries Over Time</h3>
          <div className="h-[300px]">
            {chartData.queries ? (
              <Line data={chartData.queries} options={lineChartOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">
                No data available
              </div>
            )}
          </div>
        </div>

        {/* Validations Over Time - Bar Chart */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">Expert Validations</h3>
          <div className="h-[300px]">
            {chartData.validations ? (
              <Bar data={chartData.validations} options={barChartOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">
                No data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Top Topics - Doughnut Chart */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold mb-4">Top Queried Topics</h3>
        <div className="h-[300px]">
          {chartData.topics ? (
            <Doughnut data={chartData.topics} options={doughnutOptions} />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              No topic data available
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
