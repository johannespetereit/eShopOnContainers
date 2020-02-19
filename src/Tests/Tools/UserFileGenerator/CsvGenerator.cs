using System;
using System.Collections.Generic;
using System.Text;

namespace UserFileGenerator
{
    class CsvGenerator
    {
        public string GetHeaders()
        {
            return string.Join(",", new string[]
            {
                "cardholdername","cardnumber","cardtype","city","country","email","expiration","lastname","name","phonenumber","username","zipcode","state","street","securitynumber","normalizedemail","normalizedusername","password"
            });
        }

        private string CleanupCommas(string str)
        {
            return str?.Replace(",", "");
        }
        public string GetLine(User user)
        {
            return string.Join(",", new string[]
            {
                CleanupCommas(user.CardHolderName),
                CleanupCommas(user.CardNumber),
                CleanupCommas(user.CardType.ToString()),
                CleanupCommas(user.City),
                CleanupCommas(user.Country),
                CleanupCommas(user.Email),
                CleanupCommas(user.Expiration.ToString(@"MM\/yy")),
                CleanupCommas(user.LastName),
                CleanupCommas(user.Name),
                CleanupCommas(user.PhoneNumber),
                CleanupCommas(user.UserName),
                CleanupCommas(user.ZipCode),
                CleanupCommas(user.State),
                CleanupCommas(user.Street),
                CleanupCommas(user.SecurityNumber),
                CleanupCommas(user.NormalizedEmail),
                CleanupCommas(user.NormalizedUserName),
                CleanupCommas(user.Password)
            });
        }
    }
}
