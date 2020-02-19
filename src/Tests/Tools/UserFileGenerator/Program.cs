using System;
using System.IO;
using System.Linq;
using System.Text;

namespace UserFileGenerator
{
    class Program
    {
        static void Main(string[] args)
        {
            //if (args.Length != 2 || !File.Exists(args[0]) || int.TryParse(args[1], out _))
            //{
            //    PrintHelp();
            //    return;
            //}
            int count;
            if (args.Length < 1 || !int.TryParse(args[0], out count))
            {
                count = 10;
            }

            var users = new UserGenerator().GetUsers(count);
            var csvGenerator = new CsvGenerator();
            var builder = new StringBuilder();
            builder.AppendLine(csvGenerator.GetHeaders());
            foreach (var user in users) { 
                builder.AppendLine(csvGenerator.GetLine(user));
            }
            Console.WriteLine(builder.ToString());
        }

        private static void PrintHelp()
        {
            Console.WriteLine("Usage: UserfileGenerator.exe pathToCsv count");
        }
    }
}
