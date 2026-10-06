import React from 'react';
import { Document, Page, Text, View, StyleSheet, PDFDownloadLink } from '@react-pdf/renderer';
import { TripPlan } from '../../types/trip';
import { format } from 'date-fns';

// Define styles for PDF
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#ffffff',
    padding: 30,
    fontSize: 12,
    fontFamily: 'Helvetica',
  },
  header: {
    marginBottom: 20,
    textAlign: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#2563eb',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 5,
    color: '#374151',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#1f2937',
    borderBottom: '1 solid #e5e7eb',
    paddingBottom: 5,
  },
  row: {
    flexDirection: 'row',
    marginBottom: 5,
  },
  label: {
    fontWeight: 'bold',
    width: '30%',
    color: '#374151',
  },
  value: {
    width: '70%',
    color: '#6b7280',
  },
  dayHeader: {
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 8,
    color: '#1f2937',
    backgroundColor: '#f3f4f6',
    padding: 8,
  },
  activity: {
    marginBottom: 8,
    paddingLeft: 10,
  },
  activityName: {
    fontWeight: 'bold',
    marginBottom: 2,
    color: '#374151',
  },
  activityDetails: {
    fontSize: 10,
    color: '#6b7280',
    marginBottom: 2,
  },
  costSection: {
    backgroundColor: '#f9fafb',
    padding: 15,
    marginTop: 10,
  },
  costRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  costLabel: {
    fontWeight: 'bold',
    color: '#374151',
  },
  costValue: {
    color: '#059669',
    fontWeight: 'bold',
  },
  totalCost: {
    borderTop: '1 solid #d1d5db',
    paddingTop: 8,
    marginTop: 8,
  },
  budgetStatus: {
    textAlign: 'center',
    padding: 10,
    marginTop: 10,
    fontSize: 14,
    fontWeight: 'bold',
  },
  withinBudget: {
    backgroundColor: '#d1fae5',
    color: '#065f46',
  },
  overBudget: {
    backgroundColor: '#fee2e2',
    color: '#991b1b',
  },
  slightlyOverBudget: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
  },
});

interface PDFDocumentProps {
  tripPlan: TripPlan;
}

const TripPlanDocument: React.FC<PDFDocumentProps> = ({ tripPlan }) => {
  const formatCurrency = (amount: number) => `₹${amount.toLocaleString('en-IN')}`;
  
  const getBudgetStatusStyle = (status: string) => {
    switch (status) {
      case 'Within Budget':
        return styles.withinBudget;
      case 'Over Budget':
        return styles.overBudget;
      case 'Slightly Over Budget':
        return styles.slightlyOverBudget;
      default:
        return styles.withinBudget;
    }
  };

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Trip Itinerary</Text>
          <Text style={styles.subtitle}>{tripPlan.preferences.destination}</Text>
          <Text style={styles.subtitle}>
            {format(new Date(tripPlan.preferences.startDate), 'MMM dd, yyyy')} - {format(new Date(tripPlan.preferences.endDate), 'MMM dd, yyyy')}
          </Text>
        </View>

        {/* Trip Overview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Trip Overview</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Destination:</Text>
            <Text style={styles.value}>{tripPlan.preferences.destination}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Travel Days:</Text>
            <Text style={styles.value}>{tripPlan.preferences.travelDays} days</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Travel Type:</Text>
            <Text style={styles.value}>{tripPlan.preferences.travelType}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Budget Preference:</Text>
            <Text style={styles.value}>{tripPlan.preferences.budgetPreference}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Max Budget:</Text>
            <Text style={styles.value}>{formatCurrency(tripPlan.preferences.maxBudgetInr)}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Interests:</Text>
            <Text style={styles.value}>{tripPlan.preferences.interests.join(', ')}</Text>
          </View>
        </View>

        {/* Cost Breakdown */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cost Breakdown</Text>
          <View style={styles.costSection}>
            <View style={styles.costRow}>
              <Text style={styles.costLabel}>Flights:</Text>
              <Text style={styles.costValue}>{formatCurrency(tripPlan.costBreakdown.flightCostInr)}</Text>
            </View>
            <View style={styles.costRow}>
              <Text style={styles.costLabel}>Hotels:</Text>
              <Text style={styles.costValue}>{formatCurrency(tripPlan.costBreakdown.hotelCostInr)}</Text>
            </View>
            <View style={styles.costRow}>
              <Text style={styles.costLabel}>Attractions:</Text>
              <Text style={styles.costValue}>{formatCurrency(tripPlan.costBreakdown.attractionsCostInr)}</Text>
            </View>
            <View style={styles.costRow}>
              <Text style={styles.costLabel}>Events:</Text>
              <Text style={styles.costValue}>{formatCurrency(tripPlan.costBreakdown.eventsCostInr)}</Text>
            </View>
            <View style={styles.costRow}>
              <Text style={styles.costLabel}>Local Expenses:</Text>
              <Text style={styles.costValue}>{formatCurrency(tripPlan.costBreakdown.localExpensesInr)}</Text>
            </View>
            <View style={[styles.costRow, styles.totalCost]}>
              <Text style={styles.costLabel}>Total Cost:</Text>
              <Text style={styles.costValue}>{formatCurrency(tripPlan.costBreakdown.totalCostInr)}</Text>
            </View>
          </View>
        </View>

        {/* Budget Status */}
        <View style={[styles.budgetStatus, getBudgetStatusStyle(tripPlan.budgetStatus.status)]}>
          <Text>{tripPlan.budgetStatus.status}</Text>
          {tripPlan.budgetStatus.differenceInr !== 0 && (
            <Text>
              {tripPlan.budgetStatus.differenceInr > 0 ? 'Over by: ' : 'Under by: '}
              {formatCurrency(Math.abs(tripPlan.budgetStatus.differenceInr))}
            </Text>
          )}
        </View>

        {/* Daily Itinerary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Daily Itinerary</Text>
          {tripPlan.itinerary.days.map((day) => (
            <View key={day.dayNumber}>
              <Text style={styles.dayHeader}>
                Day {day.dayNumber} - {format(new Date(day.date), 'EEEE, MMM dd, yyyy')}
              </Text>
              <View style={styles.row}>
                <Text style={styles.label}>Weather:</Text>
                <Text style={styles.value}>
                  {day.weather.condition} - {day.weather.description}
                  {day.weather.temperatureHigh && day.weather.temperatureLow && 
                    ` (${day.weather.temperatureLow}°C - ${day.weather.temperatureHigh}°C)`
                  }
                </Text>
              </View>
              <View style={styles.row}>
                <Text style={styles.label}>Daily Cost:</Text>
                <Text style={styles.value}>{formatCurrency(day.dailyCostInr)}</Text>
              </View>
              
              {day.activities.map((activity, index) => (
                <View key={index} style={styles.activity}>
                  <Text style={styles.activityName}>{activity.name}</Text>
                  <Text style={styles.activityDetails}>
                    Type: {activity.activityType} | Duration: {activity.durationHours}h | Cost: {formatCurrency(activity.costInr)}
                  </Text>
                  {activity.location && (
                    <Text style={styles.activityDetails}>Location: {activity.location}</Text>
                  )}
                  <Text style={styles.activityDetails}>{activity.description}</Text>
                  {activity.startTime && activity.endTime && (
                    <Text style={styles.activityDetails}>
                      Time: {activity.startTime} - {activity.endTime}
                    </Text>
                  )}
                </View>
              ))}
            </View>
          ))}
        </View>

        {/* Budget Suggestions */}
        {tripPlan.budgetStatus.suggestions.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Budget Suggestions</Text>
            {tripPlan.budgetStatus.suggestions.map((suggestion, index) => (
              <Text key={index} style={styles.value}>• {suggestion}</Text>
            ))}
          </View>
        )}
      </Page>
    </Document>
  );
};

interface PDFExporterProps {
  tripPlan: TripPlan;
  fileName?: string;
  className?: string;
  children?: React.ReactNode;
}

const PDFExporter: React.FC<PDFExporterProps> = ({ 
  tripPlan, 
  fileName = `trip-${tripPlan.preferences.destination}-${format(new Date(), 'yyyy-MM-dd')}.pdf`,
  className = "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",
  children = "Download PDF"
}) => {
  return (
    <PDFDownloadLink
      document={<TripPlanDocument tripPlan={tripPlan} />}
      fileName={fileName}
      className={className}
    >
      {({ blob, url, loading, error }) => {
        if (loading) return 'Generating PDF...';
        if (error) return 'Error generating PDF';
        return children;
      }}
    </PDFDownloadLink>
  );
};

export default PDFExporter;