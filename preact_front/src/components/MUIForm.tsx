// src/components/MUIForm.tsx
import { h } from 'preact';
import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Button,
  Box,
  Autocomplete,
  Chip,
} from '@mui/material';
import { useState, useEffect } from 'preact/hooks';

interface FieldConfig {
  name: string;
  label: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'multiselect';
  required?: boolean;
}

interface ReferenceData {
  subcategories: any[];
  subregions: any[];
  sweetness: any[];
  foods: any[];
  varietals: any[];
}

interface MUIFormProps {
  schema: FieldConfig[];
  onSubmit: (data: Record<string, any>) => void;
  initialValues?: Record<string, any>;
  disabled?: boolean;
  references: ReferenceData; // ← получаем справочники извне
}

export const MUIForm = ({ schema, onSubmit, initialValues = {}, disabled = false, references }: MUIFormProps) => {
  const [values, setValues] = useState<Record<string, any>>(initialValues);

  useEffect(() => {
    setValues(initialValues);
  }, [initialValues]);

  const handleChange = (name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: Event) => {
    e.preventDefault();
    onSubmit(values);
  };

  // Маппинг поля → справочник
  const getOptions = (fieldName: string) => {
    switch (fieldName) {
      case 'subcategory_id': return references.subcategories;
      case 'subregion_id': return references.subregions;
      case 'sweetness_id': return references.sweetness;
      case 'foods': return references.foods;
      case 'varietals': return references.varietals;
      default: return [];
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {schema.map(field => {
        const fieldOptions = getOptions(field.name);

        if (field.type === 'boolean') {
          return (
            <FormControlLabel
              key={field.name}
              control={
                <Checkbox
                  checked={!!values[field.name]}
                  onChange={e => handleChange(field.name, e.target.checked)}
                />
              }
              label={field.label}
            />
          );
        }

        if (field.type === 'select') {
          return (
            <FormControl key={field.name} fullWidth>
              <InputLabel>{field.label}</InputLabel>
              <Select
                value={values[field.name] || ''}
                onChange={e => handleChange(field.name, e.target.value)}
                label={field.label}
                required={field.required}
                MenuProps={{ style: { zIndex: 2001 } }}
              >
                <MenuItem value="">—</MenuItem>
                {fieldOptions.map(opt => (
                  <MenuItem key={opt.id} value={opt.id}>
                    {opt.name || opt.title || String(opt.id)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          );
        }

        if (field.type === 'multiselect') {
          return (
            <Autocomplete
              key={field.name}
              multiple
              options={fieldOptions}
              getOptionLabel={(opt) => opt.name || opt.title || String(opt.id)}
              value={fieldOptions.filter(opt => values[field.name]?.includes(opt.id)) || []}
              onChange={(e, newValue) => {
                handleChange(field.name, newValue.map(opt => opt.id));
              }}
              renderInput={(params) => <TextField {...params} label={field.label} />}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    variant="outlined"
                    label={option.name || option.title}
                    {...getTagProps({ index })}
                  />
                ))
              }
              PopperProps={{ style: { zIndex: 2001 } }}
            />
          );
        }

        return (
          <TextField
            key={field.name}
            label={field.label}
            type={field.type}
            value={values[field.name] || ''}
            onChange={e => handleChange(field.name, e.target.value)}
            required={field.required}
            disabled={disabled}
          />
        );
      })}

      <Button type="submit" variant="contained" disabled={disabled}>
        {disabled ? 'Отправка...' : 'Сохранить'}
      </Button>
    </Box>
  );
};