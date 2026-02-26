import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { HistogramData } from '@/types';

interface HistogramChartProps {
  data: HistogramData;
}

export default function HistogramChart({ data }: HistogramChartProps) {
  const chartData = data.histogram.map((item) => ({
    range: `${item.range_min.toFixed(1)}-${item.range_max.toFixed(1)}`,
    건수: item.count,
    비율: item.percentage.toFixed(1),
  }));

  // 색상 그라데이션
  const getColor = (index: number, total: number) => {
    const ratio = index / total;
    if (ratio < 0.3) return '#dc004e';
    if (ratio < 0.7) return '#ed6c02';
    return '#2e7d32';
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="range"
          label={{ value: '사정률 구간 (%)', position: 'insideBottom', offset: -5 }}
          tick={{ fontSize: 10, angle: -45, textAnchor: 'end' }}
          height={80}
        />
        <YAxis label={{ value: '건수', angle: -90, position: 'insideLeft' }} />
        <Tooltip
          formatter={(value: any, name: string) => {
            if (name === '비율') return `${value}%`;
            return value;
          }}
        />
        <Legend />
        <Bar dataKey="건수" radius={[8, 8, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getColor(index, chartData.length)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
