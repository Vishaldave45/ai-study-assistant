import * as yup from 'yup';

export const workspaceSchema = yup.object({
  name: yup
    .string()
    .required('Workspace name is required')
    .max(255, 'Workspace name cannot exceed 255 characters'),
  description: yup
    .string()
    .optional()
    .max(1000, 'Description cannot exceed 1000 characters'),
});

export type WorkspaceFormData = yup.InferType<typeof workspaceSchema>;
