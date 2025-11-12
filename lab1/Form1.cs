using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace lab1
{
    public partial class Form1 : Form
    {
        private DataGridView dataGridViewInput;
        private DataGridView dataGridViewOutput;
        private ComboBox comboBoxCase;
        private Button buttonCalculate;
        private TextBox textBoxRows;
        private TextBox textBoxCols;
        private Label labelResults;
        private Panel panelInputControls;

        public Form1()
        {
            InitializeCustomComponents();
        }

        private void InitializeCustomComponents()
        {
            this.Text = "Расчет энтропии и информации";
            this.Size = new Size(1200, 800);
            this.StartPosition = FormStartPosition.CenterScreen;

            // Case selection
            var labelCase = new Label
            {
                Text = "Выберите случай:",
                Location = new Point(20, 20),
                Size = new Size(120, 25)
            };
            this.Controls.Add(labelCase);

            comboBoxCase = new ComboBox
            {
                Location = new Point(150, 20),
                Size = new Size(400, 25),
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            comboBoxCase.Items.AddRange(new string[] {
                "a. Матрица совместных вероятностей P(AB)",
                "b. Матрица условных вероятностей P(A/B) и ансамбль B",
                "c. Матрица условных вероятностей P(B/A) и ансамбль A"
            });
            comboBoxCase.SelectedIndex = 0;
            comboBoxCase.SelectedIndexChanged += ComboBoxCase_SelectedIndexChanged;
            this.Controls.Add(comboBoxCase);

            // Matrix size controls
            var labelSize = new Label
            {
                Text = "Размер матрицы:",
                Location = new Point(20, 60),
                Size = new Size(120, 25)
            };
            this.Controls.Add(labelSize);

            var labelRows = new Label
            {
                Text = "Строки:",
                Location = new Point(150, 60),
                Size = new Size(50, 25)
            };
            this.Controls.Add(labelRows);

            textBoxRows = new TextBox
            {
                Text = "2",
                Location = new Point(200, 60),
                Size = new Size(40, 25)
            };
            this.Controls.Add(textBoxRows);

            var labelCols = new Label
            {
                Text = "Столбцы:",
                Location = new Point(250, 60),
                Size = new Size(60, 25)
            };
            this.Controls.Add(labelCols);

            textBoxCols = new TextBox
            {
                Text = "4",
                Location = new Point(310, 60),
                Size = new Size(40, 25)
            };
            this.Controls.Add(textBoxCols);

            var buttonApplySize = new Button
            {
                Text = "Применить",
                Location = new Point(360, 60),
                Size = new Size(80, 25)
            };
            buttonApplySize.Click += ButtonApplySize_Click;
            this.Controls.Add(buttonApplySize);

            // Input panel for ensemble values
            panelInputControls = new Panel
            {
                Location = new Point(20, 100),
                Size = new Size(500, 80),
                BorderStyle = BorderStyle.FixedSingle
            };
            this.Controls.Add(panelInputControls);

            // Input data grid
            dataGridViewInput = new DataGridView
            {
                Location = new Point(20, 200),
                Size = new Size(500, 250),
                AllowUserToAddRows = false,
                AllowUserToDeleteRows = false
            };
            this.Controls.Add(dataGridViewInput);

            // Calculate button
            buttonCalculate = new Button
            {
                Text = "Рассчитать",
                Location = new Point(20, 470),
                Size = new Size(120, 35),
                Font = new Font("Arial", 10, FontStyle.Bold)
            };
            buttonCalculate.Click += ButtonCalculate_Click;
            this.Controls.Add(buttonCalculate);

            // Results label
            labelResults = new Label
            {
                Text = "Результаты:",
                Location = new Point(550, 20),
                Size = new Size(600, 25),
                Font = new Font("Arial", 11, FontStyle.Bold)
            };
            this.Controls.Add(labelResults);

            // Output data grid
            dataGridViewOutput = new DataGridView
            {
                Location = new Point(550, 200),
                Size = new Size(600, 250),
                ReadOnly = true
            };
            this.Controls.Add(dataGridViewOutput);

            // Initialize with default matrix
            InitializeDataGrid();
            UpdateInputControls();
        }

        private void ButtonApplySize_Click(object sender, EventArgs e)
        {
            if (int.TryParse(textBoxRows.Text, out int rows) && int.TryParse(textBoxCols.Text, out int cols))
            {
                if (rows > 0 && cols > 0)
                {
                    InitializeDataGrid();
                    UpdateInputControls();
                }
            }
        }

        private void ComboBoxCase_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateInputControls();
        }

        private void UpdateInputControls()
        {
            panelInputControls.Controls.Clear();

            int caseIndex = comboBoxCase.SelectedIndex;
            int rows = int.Parse(textBoxRows.Text);
            int cols = int.Parse(textBoxCols.Text);

            if (caseIndex == 0) // P(AB)
            {
                // No additional controls needed for joint probabilities
            }
            else if (caseIndex == 1) // P(A/B) + ensemble B
            {
                var labelB = new Label
                {
                    Text = "Ансамбль B:",
                    Location = new Point(10, 10),
                    Size = new Size(100, 20)
                };
                panelInputControls.Controls.Add(labelB);

                // Создаем отдельные поля для каждого значения ансамбля B
                double[] defaultValuesB = { 0.26, 0.14, 0.42, 0.18 };
                for (int i = 0; i < cols; i++)
                {
                    var label = new Label
                    {
                        Text = $"P(b{i + 1}):",
                        Location = new Point(10 + i * 90, 35),
                        Size = new Size(50, 20)
                    };
                    panelInputControls.Controls.Add(label);

                    var textBox = new TextBox
                    {
                        Text = i < defaultValuesB.Length ? defaultValuesB[i].ToString("F3") : "0.0",
                        Location = new Point(10 + i * 90, 55),
                        Size = new Size(80, 20),
                        Tag = $"ensembleB_{i}"
                    };
                    panelInputControls.Controls.Add(textBox);
                }
            }
            else if (caseIndex == 2) // P(B/A) + ensemble A
            {
                var labelA = new Label
                {
                    Text = "Ансамбль A:",
                    Location = new Point(10, 10),
                    Size = new Size(100, 20)
                };
                panelInputControls.Controls.Add(labelA);

                // Создаем отдельные поля для каждого значения ансамбля A
                double[] defaultValuesA = { 0.2, 0.8 };
                for (int i = 0; i < rows; i++)
                {
                    var label = new Label
                    {
                        Text = $"P(a{i + 1}):",
                        Location = new Point(10 + i * 90, 35),
                        Size = new Size(50, 20)
                    };
                    panelInputControls.Controls.Add(label);

                    var textBox = new TextBox
                    {
                        Text = i < defaultValuesA.Length ? defaultValuesA[i].ToString("F3") : "0.0",
                        Location = new Point(10 + i * 90, 55),
                        Size = new Size(80, 20),
                        Tag = $"ensembleA_{i}"
                    };
                    panelInputControls.Controls.Add(textBox);
                }
            }
        }

        private void InitializeDataGrid()
        {
            int rows = int.Parse(textBoxRows.Text);
            int cols = int.Parse(textBoxCols.Text);

            dataGridViewInput.Columns.Clear();
            dataGridViewInput.Rows.Clear();

            // Add columns
            for (int j = 0; j < cols; j++)
            {
                dataGridViewInput.Columns.Add($"col{j}", $"b{j + 1}");
            }

            // Add rows
            for (int i = 0; i < rows; i++)
            {
                dataGridViewInput.Rows.Add();
                dataGridViewInput.Rows[i].HeaderCell.Value = $"a{i + 1}";
            }

            // Set default values based on case
            SetDefaultValues();
        }

        private void SetDefaultValues()
        {
            int caseIndex = comboBoxCase.SelectedIndex;
            int rows = dataGridViewInput.Rows.Count;
            int cols = dataGridViewInput.Columns.Count;

            if (caseIndex == 0) // P(AB)
            {
                // Example values for joint probabilities
                if (rows == 2 && cols == 4)
                {
                    dataGridViewInput.Rows[0].Cells[0].Value = "0.1";
                    dataGridViewInput.Rows[0].Cells[1].Value = "0.06";
                    dataGridViewInput.Rows[0].Cells[2].Value = "0.02";
                    dataGridViewInput.Rows[0].Cells[3].Value = "0.02";
                    dataGridViewInput.Rows[1].Cells[0].Value = "0.16";
                    dataGridViewInput.Rows[1].Cells[1].Value = "0.08";
                    dataGridViewInput.Rows[1].Cells[2].Value = "0.4";
                    dataGridViewInput.Rows[1].Cells[3].Value = "0.16";
                }
            }
            else if (caseIndex == 1) // P(A/B)
            {
                // Example values for conditional probabilities P(A/B)
                if (rows == 2 && cols == 4)
                {
                    dataGridViewInput.Rows[0].Cells[0].Value = "0.5";
                    dataGridViewInput.Rows[0].Cells[1].Value = "0.3";
                    dataGridViewInput.Rows[0].Cells[2].Value = "0.1";
                    dataGridViewInput.Rows[0].Cells[3].Value = "0.1";
                    dataGridViewInput.Rows[1].Cells[0].Value = "0.2";
                    dataGridViewInput.Rows[1].Cells[1].Value = "0.1";
                    dataGridViewInput.Rows[1].Cells[2].Value = "0.5";
                    dataGridViewInput.Rows[1].Cells[3].Value = "0.2";
                }
            }
            else if (caseIndex == 2) // P(B/A)
            {
                // Example values for conditional probabilities P(B/A)
                if (rows == 2 && cols == 4)
                {
                    dataGridViewInput.Rows[0].Cells[0].Value = "0.3846";
                    dataGridViewInput.Rows[0].Cells[1].Value = "0.4286";
                    dataGridViewInput.Rows[0].Cells[2].Value = "0.0476";
                    dataGridViewInput.Rows[0].Cells[3].Value = "0.1111";
                    dataGridViewInput.Rows[1].Cells[0].Value = "0.6154";
                    dataGridViewInput.Rows[1].Cells[1].Value = "0.5714";
                    dataGridViewInput.Rows[1].Cells[2].Value = "0.9524";
                    dataGridViewInput.Rows[1].Cells[3].Value = "0.8889";
                }
            }
        }

        private void ButtonCalculate_Click(object sender, EventArgs e)
        {
            try
            {
                CalculateProbabilities();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка: {ex.Message}", "Ошибка расчета", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void CalculateProbabilities()
        {
            int caseIndex = comboBoxCase.SelectedIndex;
            int rows = dataGridViewInput.Rows.Count;
            int cols = dataGridViewInput.Columns.Count;

            double[,] inputMatrix = new double[rows, cols];
            double[]? ensembleA = null;
            double[]? ensembleB = null;

            // Parse input matrix
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    if (dataGridViewInput.Rows[i].Cells[j].Value == null)
                    {
                        throw new Exception($"Пустое значение в ячейке [{i + 1},{j + 1}]");
                    }

                    string cellValue = dataGridViewInput.Rows[i].Cells[j].Value?.ToString() ?? "";
                    // Replace comma with dot for parsing
                    cellValue = cellValue.Replace(',', '.');

                    if (!double.TryParse(cellValue, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double value))
                    {
                        throw new Exception($"Неверное значение в ячейке [{i + 1},{j + 1}]: {dataGridViewInput.Rows[i].Cells[j].Value}");
                    }
                    inputMatrix[i, j] = value;
                }
            }

            // Parse ensemble values based on case
            if (caseIndex == 1) // P(A/B) + ensemble B
            {
                ensembleB = ParseEnsembleFromCells("ensembleB", cols, "B");
            }
            else if (caseIndex == 2) // P(B/A) + ensemble A
            {
                ensembleA = ParseEnsembleFromCells("ensembleA", rows, "A");
            }

            // Calculate probabilities based on case
            ProbabilityCalculator calculator = new ProbabilityCalculator();
            CalculationResult result = calculator.Calculate(caseIndex, inputMatrix, ensembleA, ensembleB);

            // Display results
            DisplayResults(result);
        }

        private double[] ParseEnsembleFromCells(string ensemblePrefix, int expectedLength, string ensembleName)
        {
            var values = new double[expectedLength];

            for (int i = 0; i < expectedLength; i++)
            {
                var textBox = panelInputControls.Controls.OfType<TextBox>()
                    .FirstOrDefault(t => t.Tag?.ToString() == $"{ensemblePrefix}_{i}");

                if (textBox == null)
                {
                    throw new Exception($"Не найдено поле для {ensembleName}[{i}]");
                }

                string cellValue = textBox.Text.Trim();
                cellValue = cellValue.Replace(',', '.');

                if (!double.TryParse(cellValue, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double value))
                {
                    throw new Exception($"Неверное значение в поле {ensembleName}[{i + 1}]: {textBox.Text}");
                }

                if (value < 0)
                {
                    throw new Exception($"Значение {ensembleName}[{i + 1}] не может быть отрицательным: {value}");
                }

                values[i] = value;
            }

            double sum = values.Sum();
            if (Math.Abs(sum - 1.0) > 0.001)
            {
                throw new Exception($"Сумма вероятностей ансамбля {ensembleName} должна быть равна 1.0 (получено {sum:F4})");
            }

            return values;
        }

        private double[] ParseEnsemble(string text, int expectedLength, string ensembleName)
        {
            var values = text.Split(',')
                .Select(s => s.Trim())
                .Where(s => !string.IsNullOrEmpty(s))
                .Select(s => double.Parse(s.Replace(',', '.'), System.Globalization.CultureInfo.InvariantCulture))
                .ToArray();

            if (values.Length != expectedLength)
            {
                throw new Exception($"Ансамбль {ensembleName} должен содержать {expectedLength} значений");
            }

            double sum = values.Sum();
            if (Math.Abs(sum - 1.0) > 0.001)
            {
                throw new Exception($"Сумма вероятностей ансамбля {ensembleName} должна быть равна 1.0 (получено {sum})");
            }

            return values;
        }

        private void DisplayResults(CalculationResult result)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("Результаты:");
            sb.AppendLine($"Ансамбль A: {string.Join(", ", result.EnsembleA.Select(p => p.ToString("F4")))}");
            sb.AppendLine($"Ансамбль B: {string.Join(", ", result.EnsembleB.Select(p => p.ToString("F4")))}");
            sb.AppendLine($"Энтропия H(A): {result.EntropyA:F15}");
            sb.AppendLine($"Энтропия H(B): {result.EntropyB:F15}");
            sb.AppendLine($"Условная энтропия H(B|A): {result.ConditionalEntropyBA:F15}");
            sb.AppendLine($"Условная энтропия H(A|B): {result.ConditionalEntropyAB:F15}");
            sb.AppendLine($"Совместная энтропия H(A,B): {result.JointEntropy:F15}");
            sb.AppendLine($"Взаимная информация I(A,B): {result.MutualInformation:F15}");

            labelResults.Text = sb.ToString();
            labelResults.AutoSize = true;
            labelResults.MaximumSize = new Size(600, 0);

            // Display probability matrices
            DisplayProbabilityMatrix("Матрица совместных вероятностей P(a_i, b_j):", result.JointProbabilities);

            // Also display conditional probability matrices
            DisplayConditionalProbabilityMatrices(result);
        }

        private void DisplayConditionalProbabilityMatrices(CalculationResult result)
        {
            // Create a tab control to show both conditional probability matrices
            var tabControl = new TabControl
            {
                Location = new Point(550, 470),
                Size = new Size(600, 250),
                Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
            };

            // Tab for P(A|B)
            var tabAB = new TabPage("P(A|B) - Условные вероятности A при условии B");
            var dgvAB = new DataGridView
            {
                Dock = DockStyle.Fill,
                ReadOnly = true
            };
            tabAB.Controls.Add(dgvAB);
            tabControl.TabPages.Add(tabAB);

            // Tab for P(B|A)
            var tabBA = new TabPage("P(B|A) - Условные вероятности B при условии A");
            var dgvBA = new DataGridView
            {
                Dock = DockStyle.Fill,
                ReadOnly = true
            };
            tabBA.Controls.Add(dgvBA);
            tabControl.TabPages.Add(tabBA);

            // Add tab control to form if not already added
            if (!this.Controls.Contains(tabControl))
            {
                this.Controls.Add(tabControl);
            }

            // Fill P(A|B) matrix
            FillConditionalMatrix(dgvAB, result.ConditionalProbabilitiesAB, "P(A|B)");

            // Fill P(B|A) matrix
            FillConditionalMatrix(dgvBA, result.ConditionalProbabilitiesBA, "P(B|A)");
        }

        private void FillConditionalMatrix(DataGridView dgv, double[,] matrix, string title)
        {
            dgv.Columns.Clear();
            dgv.Rows.Clear();

            int rows = matrix.GetLength(0);
            int cols = matrix.GetLength(1);

            // Add columns
            for (int j = 0; j < cols; j++)
            {
                dgv.Columns.Add($"col{j}", $"b{j + 1}");
            }

            // Add rows and data
            for (int i = 0; i < rows; i++)
            {
                dgv.Rows.Add();
                dgv.Rows[i].HeaderCell.Value = $"a{i + 1}";
                for (int j = 0; j < cols; j++)
                {
                    dgv.Rows[i].Cells[j].Value = matrix[i, j].ToString("F4");
                }
            }

            // Set title
            if (dgv.Rows.Count > 0)
            {
                dgv.Rows[0].HeaderCell.Value = title;
            }
        }

        private void DisplayProbabilityMatrix(string title, double[,] matrix)
        {
            dataGridViewOutput.Columns.Clear();
            dataGridViewOutput.Rows.Clear();

            int rows = matrix.GetLength(0);
            int cols = matrix.GetLength(1);

            // Add columns
            for (int j = 0; j < cols; j++)
            {
                dataGridViewOutput.Columns.Add($"col{j}", $"b{j + 1}");
            }

            // Add rows and data
            for (int i = 0; i < rows; i++)
            {
                dataGridViewOutput.Rows.Add();
                dataGridViewOutput.Rows[i].HeaderCell.Value = $"a{i + 1}";
                for (int j = 0; j < cols; j++)
                {
                    dataGridViewOutput.Rows[i].Cells[j].Value = matrix[i, j].ToString("F4");
                }
            }

            // Add title row
            if (dataGridViewOutput.Rows.Count > 0)
            {
                dataGridViewOutput.Rows[0].HeaderCell.Value = title;
            }
        }
    }

    public class CalculationResult
    {
        public double[] EnsembleA { get; set; } = Array.Empty<double>();
        public double[] EnsembleB { get; set; } = Array.Empty<double>();
        public double EntropyA { get; set; }
        public double EntropyB { get; set; }
        public double ConditionalEntropyAB { get; set; }
        public double ConditionalEntropyBA { get; set; }
        public double JointEntropy { get; set; }
        public double MutualInformation { get; set; }
        public double[,] JointProbabilities { get; set; } = new double[0, 0];
        public double[,] ConditionalProbabilitiesAB { get; set; } = new double[0, 0];
        public double[,] ConditionalProbabilitiesBA { get; set; } = new double[0, 0];
    }

    public class ProbabilityCalculator
    {
        public CalculationResult Calculate(int caseIndex, double[,] inputMatrix, double[]? ensembleA, double[]? ensembleB)
        {
            CalculationResult result = new CalculationResult();

            switch (caseIndex)
            {
                case 0: // P(AB) - joint probabilities
                    CalculateFromJointProbabilities(inputMatrix, result);
                    break;
                case 1: // P(A/B) + ensemble B
                    if (ensembleB != null)
                        CalculateFromConditionalAB(inputMatrix, ensembleB, result);
                    break;
                case 2: // P(B/A) + ensemble A
                    if (ensembleA != null)
                        CalculateFromConditionalBA(inputMatrix, ensembleA, result);
                    break;
            }

            CalculateEntropies(result);
            return result;
        }

        private void CalculateFromJointProbabilities(double[,] jointProbabilities, CalculationResult result)
        {
            int rows = jointProbabilities.GetLength(0);
            int cols = jointProbabilities.GetLength(1);

            result.JointProbabilities = jointProbabilities;

            // Calculate ensemble A (marginal probabilities)
            result.EnsembleA = new double[rows];
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    result.EnsembleA[i] += jointProbabilities[i, j];
                }
            }

            // Calculate ensemble B (marginal probabilities)
            result.EnsembleB = new double[cols];
            for (int j = 0; j < cols; j++)
            {
                for (int i = 0; i < rows; i++)
                {
                    result.EnsembleB[j] += jointProbabilities[i, j];
                }
            }

            // Calculate conditional probabilities
            CalculateConditionalProbabilities(result);
        }

        private void CalculateFromConditionalAB(double[,] conditionalAB, double[] ensembleB, CalculationResult result)
        {
            int rows = conditionalAB.GetLength(0);
            int cols = conditionalAB.GetLength(1);

            result.ConditionalProbabilitiesAB = conditionalAB;
            result.EnsembleB = ensembleB;

            // Calculate joint probabilities: P(A,B) = P(A|B) * P(B)
            result.JointProbabilities = new double[rows, cols];
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    result.JointProbabilities[i, j] = conditionalAB[i, j] * ensembleB[j];
                }
            }

            // Calculate ensemble A
            result.EnsembleA = new double[rows];
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    result.EnsembleA[i] += result.JointProbabilities[i, j];
                }
            }

            // Calculate conditional probabilities P(B|A)
            CalculateConditionalProbabilities(result);
        }

        private void CalculateFromConditionalBA(double[,] conditionalBA, double[] ensembleA, CalculationResult result)
        {
            int rows = conditionalBA.GetLength(0);
            int cols = conditionalBA.GetLength(1);

            result.ConditionalProbabilitiesBA = conditionalBA;
            result.EnsembleA = ensembleA;

            // Calculate joint probabilities: P(A,B) = P(B|A) * P(A)
            result.JointProbabilities = new double[rows, cols];
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    result.JointProbabilities[i, j] = conditionalBA[i, j] * ensembleA[i];
                }
            }

            // Calculate ensemble B
            result.EnsembleB = new double[cols];
            for (int j = 0; j < cols; j++)
            {
                for (int i = 0; i < rows; i++)
                {
                    result.EnsembleB[j] += result.JointProbabilities[i, j];
                }
            }

            // Calculate conditional probabilities P(A|B)
            CalculateConditionalProbabilities(result);
        }

        private void CalculateConditionalProbabilities(CalculationResult result)
        {
            int rows = result.JointProbabilities.GetLength(0);
            int cols = result.JointProbabilities.GetLength(1);

            // Calculate P(A|B) - вероятность A при условии B
            result.ConditionalProbabilitiesAB = new double[rows, cols];
            for (int j = 0; j < cols; j++)
            {
                if (result.EnsembleB[j] > 0)
                {
                    for (int i = 0; i < rows; i++)
                    {
                        result.ConditionalProbabilitiesAB[i, j] = result.JointProbabilities[i, j] / result.EnsembleB[j];
                    }
                }
            }

            // Calculate P(B|A) - вероятность B при условии A
            result.ConditionalProbabilitiesBA = new double[rows, cols];
            for (int i = 0; i < rows; i++)
            {
                if (result.EnsembleA[i] > 0)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        result.ConditionalProbabilitiesBA[i, j] = result.JointProbabilities[i, j] / result.EnsembleA[i];
                    }
                }
            }
        }

        private void CalculateEntropies(CalculationResult result)
        {
            // Calculate entropy H(A)
            result.EntropyA = CalculateEntropy(result.EnsembleA);

            // Calculate entropy H(B)
            result.EntropyB = CalculateEntropy(result.EnsembleB);

            // Calculate joint entropy H(A,B)
            result.JointEntropy = CalculateJointEntropy(result.JointProbabilities);

            // Calculate conditional entropy H(B|A)
            result.ConditionalEntropyBA = CalculateConditionalEntropy(result.JointProbabilities, result.EnsembleA);

            // Calculate conditional entropy H(A|B)
            result.ConditionalEntropyAB = CalculateConditionalEntropyTransposed(result.JointProbabilities, result.EnsembleB);

            // Calculate mutual information I(A,B) = H(A) + H(B) - H(A,B)
            result.MutualInformation = result.EntropyA + result.EntropyB - result.JointEntropy;
        }

        private double CalculateEntropy(double[] probabilities)
        {
            double entropy = 0;
            foreach (double p in probabilities)
            {
                if (p > 0)
                {
                    entropy -= p * Math.Log(p, 2);
                }
            }
            return entropy;
        }

        private double CalculateJointEntropy(double[,] jointProbabilities)
        {
            double entropy = 0;
            int rows = jointProbabilities.GetLength(0);
            int cols = jointProbabilities.GetLength(1);

            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    double p = jointProbabilities[i, j];
                    if (p > 0)
                    {
                        entropy -= p * Math.Log(p, 2);
                    }
                }
            }
            return entropy;
        }

        private double CalculateConditionalEntropy(double[,] jointProbabilities, double[] marginalProbabilities)
        {
            double conditionalEntropy = 0;
            int rows = jointProbabilities.GetLength(0);
            int cols = jointProbabilities.GetLength(1);

            for (int i = 0; i < rows; i++)
            {
                if (marginalProbabilities[i] > 0)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        double p_ij = jointProbabilities[i, j];
                        if (p_ij > 0)
                        {
                            double p_j_given_i = p_ij / marginalProbabilities[i];
                            conditionalEntropy -= p_ij * Math.Log(p_j_given_i, 2);
                        }
                    }
                }
            }
            return conditionalEntropy;
        }

        private double CalculateConditionalEntropyTransposed(double[,] jointProbabilities, double[] marginalProbabilities)
        {
            double conditionalEntropy = 0;
            int rows = jointProbabilities.GetLength(0);
            int cols = jointProbabilities.GetLength(1);

            for (int j = 0; j < cols; j++)
            {
                if (marginalProbabilities[j] > 0)
                {
                    for (int i = 0; i < rows; i++)
                    {
                        double p_ij = jointProbabilities[i, j];
                        if (p_ij > 0)
                        {
                            double p_i_given_j = p_ij / marginalProbabilities[j];
                            conditionalEntropy -= p_ij * Math.Log(p_i_given_j, 2);
                        }
                    }
                }
            }
            return conditionalEntropy;
        }
    }
}
