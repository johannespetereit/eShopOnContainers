using Bogus;
using System;
using System.Collections.Generic;
using System.Text;

namespace UserFileGenerator
{
    class UserGenerator
    {
        public IEnumerable<User> GetUsers(int count)
        {
            var faker = new Faker<User>()
                .StrictMode(true)
                .RuleFor(u => u.CardHolderName, f => f.Name.FullName())
                .RuleFor(u => u.CardNumber, f => {
                    var number = f.Finance.CreditCardNumber();
                    if (number.Length > 19)
                        number = number.Remove(19);
                    return number;
                })
                .RuleFor(u => u.CardType, f => f.Random.Number(1, 3))
                .RuleFor(u => u.City, f => f.Address.City())
                .RuleFor(u => u.Country, f => f.Address.Country())
                .RuleFor(u => u.Expiration, f => f.Date.Future())
                .RuleFor(u => u.LastName, (f, u) => u.CardHolderName.Substring(u.CardHolderName.LastIndexOf(" ") + 1))
                .RuleFor(u => u.Name, (f, u) => u.CardHolderName)
                .RuleFor(u => u.PhoneNumber, f => f.Person.Phone)
                .RuleFor(u => u.UserName, f => f.Person.UserName + f.IndexGlobal)
                .RuleFor(u => u.Email, f => f.Person.Email)
                .RuleFor(u => u.ZipCode, f => f.Address.ZipCode())
                .RuleFor(u => u.State, f => f.Address.StateAbbr())
                .RuleFor(u => u.Street, f => f.Address.StreetAddress())
                .RuleFor(u => u.SecurityNumber, f => f.Finance.CreditCardCvv())
                .RuleFor(u => u.Password, f => f.Random.Word().Replace(" ","").Replace("-","_") + f.Random.Number(9999))
                ;
            return faker.Generate(count);
        }
    }
}
