import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TrendChartProps {
  data: Array<{
    date: string;
    count: number;
    avg_rate: number;
    std_rate: number;
  }>;
}

export default function TrendChart({ data }: TrendChartProps) {
  const chartData = data.map((item) => ({
    date: item.date,
    건수: item.count,
    평균사정률: item.avg_rate ? item.avg_rate.toFixed(2) : null,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => {
            const date = new Date(value);
            return `${date.getMonth() + 1}/${date.getDate()}`;
          }}
        />
        <YAxis yAxisId="left" label={{ value: '건수', angle: -90, position: 'insideLeft' }} />
        <YAxis
          yAxisId="right"
          orientation="right"
          label={{ value: '평균 사정률 (%)', angle: 90, position: 'insideRight' }}
        />
        <Tooltip
          labelFormatter={(value) => `날짜: ${value}`}
          formatter={(value: any) => {
            return typeof value === 'number' ? value.toLocaleString() : value;
          }}
        />
        <Legend />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="건수"
          stroke="#1976d2"
          strokeWidth={2}
          dot={false}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="평균사정률"
          stroke="#dc004e"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
