import tkinter as tk
from tkinter import ttk, messagebox
import boto3
from botocore.exceptions import ClientError
import requests

class S3UI:
    def __init__(self, root):
        self.root = root
        self.root.title("IONOS info")
        self.build_input_window()

    def build_input_window(self):
        self.root.geometry("270x350+100+100")  # Set size for the input window

        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Use a frame for the key inputs for better control
        key_frame = tk.Frame(self.root)
        key_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='ew')

        tk.Label(key_frame, text="AWS Key:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.key_entry = tk.Entry(key_frame)
        self.key_entry.grid(row=0, column=1, padx=5, pady=5)

        # Insert default value for AWS Key
        default_aws_key = ""  # Replace with your actual default key
        self.key_entry.insert(0, default_aws_key)

        tk.Label(key_frame, text="Secret Key:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.secret_key_entry = tk.Entry(key_frame, show='*')
        self.secret_key_entry.grid(row=1, column=1, padx=5, pady=5)

        # Insert default value for Secret Key
        default_secret_key = ""  # Replace with your actual default secret key
        self.secret_key_entry.insert(0, default_secret_key)

        # Use a frame for the listbox and scrollbar
        listbox_frame = tk.Frame(self.root)
        listbox_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky='ew')

        tk.Label(listbox_frame, text="Buckets:").grid(row=0, column=0, padx=5, pady=5, sticky='nw')

        # Create vertical scrollbar
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)

        # Create Listbox with the scrollbar
        self.bucket_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
        self.bucket_listbox.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        scrollbar.config(command=self.bucket_listbox.yview)
        scrollbar.grid(row=0, column=2, padx=5, pady=5, sticky='ns')

        # Configure grid weights for expanding elements
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(1, weight=4)  # More weight to listbox
        listbox_frame.grid_rowconfigure(0, weight=1)

        # Center-align buttons by adjusting grid columnspan
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.load_buckets_button = tk.Button(button_frame, text="Load Buckets", command=self.load_buckets)
        self.load_buckets_button.grid(row=0, column=0, padx=(60, 10))  # Increase the right padding

        tk.Button(button_frame, text="Submit", command=self.submit).grid(row=0, column=1, padx=5)

    def load_buckets(self):
        self.bucket_listbox.delete(0, tk.END)  # Clear previous entries

        key = self.key_entry.get()
        secret_key = self.secret_key_entry.get()

        api_endpoints = ['https://s3.eu-central-3.ionoscloud.com', 'https://s3.eu-central-1.ionoscloud.com']
        buckets = set()

        for endpoint in api_endpoints:
            try:
                s3client = boto3.client('s3',
                                        aws_access_key_id=key,
                                        aws_secret_access_key=secret_key,
                                        endpoint_url=endpoint)

                response = s3client.list_buckets()
                for bucket in response['Buckets']:
                    buckets.add(bucket['Name'])

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load buckets from {endpoint}: {str(e)}")

        # Convert the set to a sorted list
        sorted_buckets = sorted(buckets)

        # Insert "All Buckets" at the start of the list
        sorted_buckets.insert(0, "All Buckets")

        # Add sorted buckets to the Listbox
        for bucket in sorted_buckets:
            self.bucket_listbox.insert(tk.END, bucket)

    def submit(self):
        selected_indices = self.bucket_listbox.curselection()
        selected_buckets = [self.bucket_listbox.get(i) for i in selected_indices]
        
        if "All Buckets" in selected_buckets:
            selected_buckets = ["All Buckets"]
        
        key = self.key_entry.get()
        secret_key = self.secret_key_entry.get()

        try:
            self.build_table_window(selected_buckets, key, secret_key)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get bucket info: {str(e)}")

    def build_table_window(self, selected_buckets, key, secret_key):
        self.root.geometry("1600x400+50+50")  # Set size for the input window
        for widget in self.root.winfo_children():
            widget.destroy()

        columns = ("Bucket Name", "# Objects", "# Objects with Versioning", "Location", "Versioning", "Object Lock")

        tree = ttk.Treeview(self.root, columns=columns, show='headings')
        tree.heading("Bucket Name", text="Bucket Name")
        tree.heading("# Objects", text="# Objects")
        tree.heading("# Objects with Versioning", text="# Objects with Versioning")
        tree.heading("Location", text="Location")
        tree.heading("Versioning", text="Versioning")
        tree.heading("Object Lock", text="Object Lock")

        self.query_and_populate_tree(tree, selected_buckets, key, secret_key)

        tree.pack(expand=True, fill='both')
        tk.Button(self.root, text="Back", command=self.build_input_window).pack(side='left', padx=5, pady=5)
        tk.Button(self.root, text="Close", command=self.root.quit).pack(side='right', padx=5, pady=5)

    def query_and_populate_tree(self, tree, buckets, apiKeyi, apiSecretKeyi):
        api_endpoints = ['https://s3.eu-central-3.ionoscloud.com', 'https://s3.eu-central-1.ionoscloud.com']

        for ep in api_endpoints:
            s3client = boto3.client('s3',
                aws_access_key_id=apiKeyi,
                aws_secret_access_key=apiSecretKeyi,
                endpoint_url=ep
            )
            s3resource = boto3.resource('s3',
                  aws_access_key_id=apiKeyi,
                  aws_secret_access_key=apiSecretKeyi,
                  endpoint_url=ep
            )
            all_buckets = s3client.list_buckets()

            # Gather all data based on current selection
            if "All Buckets" in buckets:
                bucket_names = [bucket['Name'] for bucket in all_buckets['Buckets']]
            else:
                bucket_names = [bucket for bucket in buckets if bucket in [b['Name'] for b in all_buckets['Buckets']]]

            for bucket_name in bucket_names:
                bucket42 = s3resource.Bucket(bucket_name)
                reduced_url = ep.replace("https://", ".")
                urlBucket = "https://" + bucket_name + reduced_url

                try:
                    resUrlBucket = requests.get(urlBucket, allow_redirects=False)
                except ClientError as e:
                    print(f"Failed to get URL for bucket {bucket42.name}: {e}")
                    continue

                if resUrlBucket.is_redirect:
                    nospliturl = resUrlBucket.headers['Location']
                    nocol = nospliturl.split(":")
                    realurl = nocol[1].split(".", 1)
                    secondlevel = realurl[1]

                    s3resource = boto3.resource('s3',
                        aws_access_key_id=apiKeyi,
                        aws_secret_access_key=apiSecretKeyi,
                        endpoint_url="https://" + secondlevel
                    )
                    bucket42 = s3resource.Bucket(bucket_name)

                c0 = sum(1 for _ in bucket42.objects.all())

                object_count = 0
                try:
                    paginator = s3resource.meta.client.get_paginator('list_object_versions')
                    for page in paginator.paginate(Bucket=bucket42.name):
                        object_count += len(page.get('Versions', []))
                        object_count += len(page.get('DeleteMarkers', []))
                except ClientError as e:
                    print(f"Failed to list object versions for bucket {bucket42.name}: {e}")

                location_response = s3resource.meta.client.get_bucket_location(Bucket=bucket42.name)
                location = location_response['LocationConstraint'] or 's3.eu-central-1.ionoscloud.com'

                versioning = s3resource.BucketVersioning(bucket42.name)
                versioning_status = versioning.status or 'Disabled'

                try:
                    object_lock = s3resource.meta.client.get_object_lock_configuration(Bucket=bucket42.name)
                    object_lock_enabled = bool(object_lock.get('ObjectLockConfiguration'))
                except ClientError:
                    object_lock_enabled = False

                tree.insert("", "end", values=(
                    bucket42.name, c0, object_count, location, versioning_status, object_lock_enabled
                ))


if __name__ == "__main__":
    root = tk.Tk()
    app = S3UI(root)
    root.mainloop()