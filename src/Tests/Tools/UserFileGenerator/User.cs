using System;

namespace UserFileGenerator
{
    class User
    {
        public string CardHolderName { get; set; }
        public string CardNumber { get; set; }
        public int CardType { get; set; }
        public string City { get; set; }
        public string Country { get; set; }
        public string Email { get; set; }
        public DateTime Expiration { get; set; }
        public string LastName { get; set; }
        public string Name { get; set; }
        public string PhoneNumber { get; set; }
        public string UserName { get; set; }
        public string ZipCode { get; set; }
        public string State { get; set; }
        public string Street { get; set; }
        public string SecurityNumber { get; set; }
        public string NormalizedEmail => Email.ToUpperInvariant();
        public string NormalizedUserName => UserName.ToUpperInvariant();
        public string Password { get; set; }
    }
}
