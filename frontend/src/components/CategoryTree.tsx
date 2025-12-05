import { useState } from 'react';
import { Category } from '../types';

interface CategoryTreeProps {
    categories: Category[];
    onSelect: (category: Category) => void;
    selectedIds: string[];
}

interface CategoryNodeProps {
    category: Category;
    onSelect: (category: Category) => void;
    selectedIds: string[];
    level: number;
}

const CategoryNode = ({ category, onSelect, selectedIds, level }: CategoryNodeProps) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const hasChildren = category.children && category.children.length > 0;
    const isSelected = selectedIds.includes(category.id);

    const handleToggle = (e: React.MouseEvent) => {
        e.stopPropagation();
        setIsExpanded(!isExpanded);
    };

    const handleSelect = (e: React.MouseEvent) => {
        e.stopPropagation();
        onSelect(category);
    };

    return (
        <div className="select-none">
            <div
                className={`
          flex items-center py-1 px-2 hover:bg-gray-100 cursor-pointer rounded
          ${isSelected ? 'bg-blue-50 text-blue-700' : ''}
        `}
                style={{ paddingLeft: `${level * 16 + 8}px` }}
                onClick={handleSelect}
            >
                {hasChildren ? (
                    <button
                        type="button"
                        onClick={handleToggle}
                        className="mr-2 w-4 h-4 flex items-center justify-center text-gray-500 hover:text-gray-700 focus:outline-none"
                    >
                        {isExpanded ? '▼' : '▶'}
                    </button>
                ) : (
                    <span className="w-4 mr-2" /> // Spacer
                )}

                <span className="text-sm">
                    {category.name}
                    {category.vinted_id && (
                        <span className="ml-2 text-xs text-gray-400">({category.vinted_id})</span>
                    )}
                </span>
            </div>

            {isExpanded && hasChildren && (
                <div>
                    {category.children!.map((child) => (
                        <CategoryNode
                            key={child.id}
                            category={child}
                            onSelect={onSelect}
                            selectedIds={selectedIds}
                            level={level + 1}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default function CategoryTree({ categories, onSelect, selectedIds }: CategoryTreeProps) {
    if (!categories || categories.length === 0) {
        return <div className="text-gray-500 text-sm p-4">No categories found.</div>;
    }

    return (
        <div className="border rounded-md max-h-96 overflow-y-auto bg-white">
            {categories.map((category) => (
                <CategoryNode
                    key={category.id}
                    category={category}
                    onSelect={onSelect}
                    selectedIds={selectedIds}
                    level={0}
                />
            ))}
        </div>
    );
}
