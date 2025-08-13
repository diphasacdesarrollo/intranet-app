from django.contrib.auth.models import User
from django.db import models

import re
import time


class SupervisedUser(models.Model):
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supervised_users")
    supervised_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supervisors",
                                        verbose_name="Vendedor")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    @property
    def supervisor_str(self):
        str = ""
        if self.supervisor.first_name:
            str += self.supervisor.first_name
            if self.supervisor.last_name:
                str += " " + self.supervisor.last_name
        else:
            str += self.supervisor.username
        return str

    @property
    def supervised_user_str(self):
        str = ""
        if self.supervised_user.first_name:
            str += self.supervised_user.first_name
            if self.supervised_user.last_name:
                str += " " + self.supervised_user.last_name
        else:
            str += self.supervised_user.username
        return str

    class Meta:
        verbose_name = "Supervisor"
        verbose_name_plural = "Supervisores"
        unique_together = [('supervisor', 'supervised_user')]

    def __str__(self):
        str = "Supervisor: "
        if self.supervisor.first_name:
            str += self.supervisor.first_name
            if self.supervisor.last_name:
                str += " " + self.supervisor.last_name
        else:
            str += self.supervisor.username
        str += "| Vendedor: "
        if self.supervised_user.first_name:
            str += self.supervised_user.first_name
            if self.supervised_user.last_name:
                str += " " + self.supervised_user.last_name
        else:
            str += self.supervised_user.username
        return str

    @staticmethod
    def get_users_by_supervisor(supervisor: User):
        supervised_users = SupervisedUser.objects.filter(supervisor=supervisor).values('supervised_user')
        return User.objects.filter(id__in=supervised_users)

    @classmethod
    def import_from_excel(cls, file) -> (int, list):
        import pandas as pd
        from main.models import Client, ClientCategory
        success_count = 0
        error_rows = []
        df = pd.read_excel(file)

        # Preprocess the columns
        df["Vendedor"] = df["Vendedor"].str.replace(" ", "", regex=True).str.lower()
        df["Ruc"] = df["Ruc"].astype(str).apply(lambda x: re.sub(r"\D", "", x))  # Keep only digits
        df["Nombre (opcional)"] = df["Nombre (opcional)"].astype(str).apply(lambda x: re.sub(r"\s+", " ", x).strip())
        df["Canal (opcional)"] = df["Canal (opcional)"].astype(str).apply(lambda x: re.sub(r"\s+", " ", x).strip())
        df["Dirección(opcional)"] = df["Dirección(opcional)"].astype(str).apply(
            lambda x: re.sub(r"\s+", " ", x).strip())

        # Iterate over each row
        for index, row in df.iterrows():
            print("-" * 50 + "ROW" + str(index+2) + "-" * 50)

            user = row["Vendedor"]
            print("Searchin for user: ", user)
            user_search = User.objects.filter(username=user).first()
            if user_search is None:
                print("User not found")
                error_rows.append('En la fila {} no se encontró el vendedor con correo {}'.format(index + 2, user))
                continue

            ruc = row["Ruc"]
            client_search = Client.objects.filter(ruc=ruc).first()
            print("Searchin for client with RUC: ", ruc)
            if client_search is None:
                print("Client not found")
                nombre = row["Nombre (opcional)"]
                direccion = row["Dirección(opcional)"]
                try:
                    print("Creating new client")
                    new_client = Client.objects.create(ruc=ruc, name=nombre, account_manager=user_search)
                    category = row["Canal (opcional)"]
                    if category is not None and category != "":
                        category_search = ClientCategory.objects.filter(name=category).first()
                        if category_search is not None:
                            print("Category found: " + category_search.name)
                            new_client.category = category_search
                            new_client.save()
                        else:
                            print("Category not found")
                            new_category = ClientCategory.objects.create(name=category)
                            new_client.category = new_category
                            new_client.save()
                except Exception as e:
                    error_rows.append('En la fila {} no se pudo crear el cliente con RUC {}. Error: {}'.format(index + 2, ruc, e))
                else:
                    if direccion:
                        try:
                            new_client.locations.create(address=direccion)
                        except Exception as e:
                            error_rows.append('En la fila {} no se pudo crear la locación para el cliente con RUC {}. Error: {}'.format(index + 2, ruc, e))
                    new_client.account_manager = user_search
                    new_client.save()
                    success_count += 1
            else:
                print("Client found")
                client_search.account_manager = user_search
                try:
                    client_search.save()
                except Exception as e:
                    error_rows.append('En la fila {} no se pudo actualizar el cliente con RUC {}. Error: {}'.format(index + 2, ruc, e))
                else:
                    success_count += 1
        return success_count, error_rows