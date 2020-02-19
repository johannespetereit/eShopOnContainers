using Bogus;
using System;
using System.Collections.Generic;
using System.Text;

namespace UserFileGenerator
{
    internal static class BogusExtensions
    {
        public static string CreditCardNumber(this Person person)
        {
            return person.Random.Long(4111111111111111, 5555555555554444).ToString();
        }
    }
}
