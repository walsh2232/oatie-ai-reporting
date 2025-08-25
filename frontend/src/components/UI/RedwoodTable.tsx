/**
 * Oracle Redwood Design System Table Component
 * WCAG 2.1 AA compliant with full accessibility support
 */
import React from 'react';
import { cn } from '../../lib/utils';

interface Column<T> {
  key: keyof T;
  header: string;
  accessor?: (item: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface RedwoodTableProps<T> {
  data: T[];
  columns: Column<T>[];
  className?: string;
  loading?: boolean;
  emptyMessage?: string;
  sortField?: keyof T;
  sortDirection?: 'asc' | 'desc';
  onSort?: (field: keyof T) => void;
  onRowClick?: (item: T, index: number) => void;
  hoverable?: boolean;
  striped?: boolean;
  compact?: boolean;
  caption?: string;
}

function RedwoodTable<T extends Record<string, any>>({
  data,
  columns,
  className,
  loading = false,
  emptyMessage = 'No data available',
  sortField,
  sortDirection,
  onSort,
  onRowClick,
  hoverable = true,
  striped = true,
  compact = false,
  caption,
}: RedwoodTableProps<T>) {
  const SortIcon = ({ column }: { column: Column<T> }) => {
    if (!column.sortable) return null;

    const isActive = sortField === column.key;
    
    return (
      <span className="ml-2 inline-flex flex-col">
        <svg
          className={cn(
            'w-3 h-3 -mb-1',
            isActive && sortDirection === 'asc' 
              ? 'text-[#ED6C02]' 
              : 'text-[#CCCCCC]'
          )}
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" />
        </svg>
        <svg
          className={cn(
            'w-3 h-3',
            isActive && sortDirection === 'desc' 
              ? 'text-[#ED6C02]' 
              : 'text-[#CCCCCC]'
          )}
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
        </svg>
      </span>
    );
  };

  const LoadingRow = () => (
    <tr>
      <td 
        colSpan={columns.length} 
        className="px-6 py-8 text-center text-[#666666]"
      >
        <div className="flex items-center justify-center gap-3">
          <svg
            className="w-5 h-5 animate-spin text-[#ED6C02]"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>Loading data...</span>
        </div>
      </td>
    </tr>
  );

  const EmptyRow = () => (
    <tr>
      <td 
        colSpan={columns.length} 
        className="px-6 py-8 text-center text-[#666666]"
      >
        <div className="flex flex-col items-center gap-2">
          <svg
            className="w-12 h-12 text-[#CCCCCC]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <span>{emptyMessage}</span>
        </div>
      </td>
    </tr>
  );

  const handleHeaderClick = (column: Column<T>) => {
    if (column.sortable && onSort) {
      onSort(column.key);
    }
  };

  const getCellAlignment = (align?: string) => {
    switch (align) {
      case 'center': return 'text-center';
      case 'right': return 'text-right';
      default: return 'text-left';
    }
  };

  return (
    <div className={cn('w-full overflow-auto', className)}>
      <table 
        className="w-full border-collapse bg-white"
        role="table"
        aria-label={caption}
      >
        {caption && (
          <caption className="sr-only">
            {caption}
          </caption>
        )}
        
        <thead>
          <tr className="border-b-2 border-[#E0E0E0]">
            {columns.map((column) => (
              <th
                key={String(column.key)}
                className={cn(
                  compact ? 'px-3 py-2' : 'px-6 py-4',
                  'text-left text-sm font-semibold text-[#333333] bg-[#F8F9FA]',
                  column.sortable && 'cursor-pointer select-none hover:bg-[#E9ECEF]',
                  getCellAlignment(column.align)
                )}
                style={{ width: column.width }}
                onClick={() => handleHeaderClick(column)}
                role="columnheader"
                tabIndex={column.sortable ? 0 : undefined}
                onKeyDown={(e) => {
                  if (column.sortable && (e.key === 'Enter' || e.key === ' ')) {
                    e.preventDefault();
                    handleHeaderClick(column);
                  }
                }}
                aria-sort={
                  column.sortable && sortField === column.key
                    ? sortDirection === 'asc' ? 'ascending' : 'descending'
                    : column.sortable ? 'none' : undefined
                }
              >
                <div className="flex items-center">
                  {column.header}
                  <SortIcon column={column} />
                </div>
              </th>
            ))}
          </tr>
        </thead>
        
        <tbody>
          {loading ? (
            <LoadingRow />
          ) : data.length === 0 ? (
            <EmptyRow />
          ) : (
            data.map((item, index) => (
              <tr
                key={index}
                className={cn(
                  'border-b border-[#E0E0E0]',
                  striped && index % 2 === 1 && 'bg-[#F8F9FA]',
                  hoverable && 'hover:bg-[#F5F5F5]',
                  onRowClick && 'cursor-pointer',
                  'transition-colors duration-150'
                )}
                onClick={() => onRowClick?.(item, index)}
                role="row"
                tabIndex={onRowClick ? 0 : undefined}
                onKeyDown={(e) => {
                  if (onRowClick && (e.key === 'Enter' || e.key === ' ')) {
                    e.preventDefault();
                    onRowClick(item, index);
                  }
                }}
              >
                {columns.map((column) => (
                  <td
                    key={String(column.key)}
                    className={cn(
                      compact ? 'px-3 py-2' : 'px-6 py-4',
                      'text-sm text-[#333333]',
                      getCellAlignment(column.align)
                    )}
                    role="cell"
                  >
                    {column.accessor 
                      ? column.accessor(item) 
                      : String(item[column.key] ?? '')
                    }
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export { RedwoodTable };
export type { RedwoodTableProps, Column };