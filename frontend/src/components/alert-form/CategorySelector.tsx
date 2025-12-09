import { useState, useEffect } from 'react';
import CheckboxTree from 'react-checkbox-tree';
import 'react-checkbox-tree/lib/react-checkbox-tree.css';
import {
  FaCheckSquare,
  FaSquare,
  FaChevronRight,
  FaChevronDown,
  FaPlusSquare,
  FaMinusSquare,
  FaFolder,
  FaFolderOpen,
  FaFile
} from 'react-icons/fa';
import type { Category } from '../../types';
import * as api from '../../services/api';

// Helper to transform Category[] to CheckboxTree nodes
const transformCategoriesToNodes = (categories: Category[]): any[] => {
  return categories.map(cat => ({
    value: cat.id,
    label: `${cat.name} (ID: ${cat.vinted_id})`,
    children: cat.children && cat.children.length > 0
      ? transformCategoriesToNodes(cat.children)
      : undefined
  }));
};

// Helper to find category by ID (recursive)
const findCategoryById = (categories: Category[], id: string): Category | undefined => {
  for (const cat of categories) {
    if (cat.id === id) return cat;
    if (cat.children) {
      const found = findCategoryById(cat.children, id);
      if (found) return found;
    }
  }
  return undefined;
};

interface CategorySelectorProps {
  countryCode: string;
  useCategoryIds: boolean;
  onUseCategoryIdsChange: (value: boolean) => void;
  catalogIds: string;
  onCatalogChange: (catalogIds: string, catalogNames: string | undefined) => void;
  inputClass: string;
}

export function CategorySelector({
  countryCode,
  useCategoryIds,
  onUseCategoryIdsChange,
  catalogIds,
  onCatalogChange,
  inputClass
}: CategorySelectorProps) {
  const [treeCategories, setTreeCategories] = useState<Category[]>([]);
  const [loadingTree, setLoadingTree] = useState(false);
  const [checkedCategories, setCheckedCategories] = useState<string[]>([]);
  const [expandedCategories, setExpandedCategories] = useState<string[]>([]);

  // Fetch category tree when country changes
  useEffect(() => {
    const fetchCategories = async () => {
      setLoadingTree(true);
      try {
        const categories = await api.getCategories(countryCode);
        setTreeCategories(categories);
      } catch (error) {
        console.error('Failed to fetch category tree:', error);
        setTreeCategories([]);
      } finally {
        setLoadingTree(false);
      }
    };

    fetchCategories();
  }, [countryCode]);

  // Update form data when checked categories change
  useEffect(() => {
    if (treeCategories.length === 0) return;

    const selectedCats = checkedCategories
      .map(id => findCategoryById(treeCategories, id))
      .filter((c): c is Category => !!c);

    const ids = selectedCats.map(c => c.vinted_id).join(',');
    const names = selectedCats.map(c => c.name).join(', ');

    onCatalogChange(ids, names || undefined);
  }, [checkedCategories, treeCategories, onCatalogChange]);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span>Categories (Optional)</span>
        <label className="text-sm font-normal inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={useCategoryIds}
            onChange={(e) => onUseCategoryIdsChange(e.target.checked)}
          />
          Enter IDs
        </label>
      </div>

      {useCategoryIds ? (
        <div className="space-y-1">
          <input
            type="text"
            placeholder="Comma-separated category IDs (e.g., 1193,1920)"
            value={catalogIds || ''}
            onChange={(e) => {
              const value = e.target.value;
              onCatalogChange(value, value ? `IDs: ${value}` : undefined);
            }}
            className={inputClass}
          />
          <small className="text-xs text-gray-500">Paste Vinted catalog IDs when you already know them.</small>
        </div>
      ) : (
        <div>
          {loadingTree ? (
            <div className="text-sm text-gray-500 p-4 border rounded bg-gray-50 text-center">
              Loading categories...
            </div>
          ) : (
            <div className="border rounded p-2 bg-white max-h-96 overflow-y-auto">
              <CheckboxTree
                nodes={transformCategoriesToNodes(treeCategories)}
                checked={checkedCategories}
                expanded={expandedCategories}
                onCheck={(checked) => setCheckedCategories(checked as string[])}
                onExpand={(expanded) => setExpandedCategories(expanded as string[])}
                icons={{
                  check: <FaCheckSquare />,
                  uncheck: <FaSquare />,
                  halfCheck: <FaMinusSquare />,
                  expandClose: <FaChevronRight />,
                  expandOpen: <FaChevronDown />,
                  expandAll: <FaPlusSquare />,
                  collapseAll: <FaMinusSquare />,
                  parentClose: <FaFolder />,
                  parentOpen: <FaFolderOpen />,
                  leaf: <FaFile />
                }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
